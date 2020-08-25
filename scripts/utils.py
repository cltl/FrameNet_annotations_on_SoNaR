from sonar_classes import Frame, FrameElement
from lxml import etree
from collections import defaultdict
import os
import pickle
import shutil

import pandas

cat_pos2fn_pos = {
    'adj' : 'A',
    'adv' : 'ADV',
    'det' : 'ART',
    'noun' : 'NUM',
    'prep' : 'PREP',
    'pron' : 'PRON',
    'verb' : 'V',
    'vg' : 'C'
}

class Lemma:
    """

    """
    def __init__(self,
                 lemma,
                 frame_label,
                 provenance,
                 language,
                 pos=None,
                 lu_id=None):
        self.lemma = lemma
        self.frame_label = frame_label
        self.provenance = provenance
        self.language = language
        self.lu_id = lu_id
        self.pos = pos
        self.lemma_pos_id = None # FrameNet provides an identifier for each lemma and pos combination

        self.short_rdf_uri = self.get_short_uri()


    def get_hover_info(self):
        return {
            'lemma': self.lemma,
            'language' : self.language,
            'pos' : self.pos,
        }

    def get_short_uri(self):
        if self.pos is not None:
            uri = f'({self.language}){self.lemma}.{self.pos}'
        else:
            uri = f'({self.language}){self.lemma}'

        return uri


    def __str__(self):
        info = [f'frame label: {self.frame_label}',
                f'lemma: {self.lemma}',
                f'pos: {self.pos}',
                f'LU ID: {self.lu_id}',
                f'provenance: {self.provenance}']

        return ' '.join(info)

class Lexeme:
    """

    """
    def __init__(self, lexeme, frame_label, provenance):
        self.lexeme = lexeme
        self.frame_label = frame_label
        self.provenance = provenance


    def __str__(self):
        info = [f'frame label: {self.frame_label}',
                f'lexeme: {self.lexeme}',
                f'provenance: {self.provenance}']

        return ' '.join(info)


def load_sonar_annotations(configuration, verbose=0):
    """
    load sonar annotations to
    frame_label -> list of Lexeme objects

    :param dict configuration: configuration (see config_files folder)

    :rtype: tuple
    :return: (mapping of frame_label -> lexeme objects,
              stats)
    """
    # load annotator information
    assert os.path.exists((configuration['path_sonar_annotator_1']))
    with open(configuration['path_sonar_annotator_1'], 'rb') as infile:
        annotator_1 = pickle.load(infile)

    assert os.path.exists((configuration['path_sonar_annotator_2']))
    with open(configuration['path_sonar_annotator_2'], 'rb') as infile:
        annotator_2 = pickle.load(infile)


    shared_keys = set(annotator_1) | set(annotator_2)
    merging_stats = {
        '# of shared_annotations' : len(shared_keys),
        '# of same frame annotations' : 0
    }

    provenance_label = 'sonar_fn_annotations'
    frame_label2lexeme_objs = defaultdict(list)
    frame_label2lemma_objs = defaultdict(list)

    for key in shared_keys:

        info_annotator_1 = annotator_1[key]
        info_annotator_2 = annotator_2[key]


        # check that both have only one frame annotated + it is the same one
        if all([len(info_annotator_1.frame) == 1,
                len(info_annotator_2.frame) == 1]):

            if info_annotator_1.frame == info_annotator_2.frame:

                text_anno_1 = info_annotator_1.predicate['text']
                text_anno_2 = info_annotator_2.predicate['text']

                lemma_anno_1 = info_annotator_1.predicate['lemma']
                lemma_anno_2 = info_annotator_2.predicate['lemma']

                pos = info_annotator_2.predicate['fn_pos']

                if all([text_anno_1 == text_anno_2,
                        lemma_anno_1 == lemma_anno_2]):
                    frame_label = list(info_annotator_1.frame)[0]

                    predicate_label = text_anno_1
                    predicate_lemma = lemma_anno_1

                    lexeme_obj = Lexeme(lexeme=predicate_label,
                                        frame_label=frame_label,
                                        provenance=provenance_label)

                    frame_label2lexeme_objs[frame_label].append(lexeme_obj)

                    lemma_obj = Lemma(lemma=predicate_lemma,
                                      pos=pos,
                                      frame_label=frame_label,
                                      provenance=provenance_label,
                                      language='Dutch',
                                      lu_id=None)

                    frame_label2lemma_objs[frame_label].append(lemma_obj)


                    merging_stats['# of same frame annotations'] += 1

                else:
                    if verbose >= 2:
                        print()
                        print(key)
                        print('predicate label differs')
                        print(text_anno_1, text_anno_2)


    if verbose:
        print()
        print(f'num of frames with at least one annotation: {len(frame_label2lexeme_objs)}')
        print(merging_stats)

    return (frame_label2lexeme_objs,
            frame_label2lemma_objs,
            merging_stats)

def load_index2term_info(naf_doc):
    """
    load index of token to corresponding lemma (from terms/term layer)

    :param lxml.etree._ElementTree naf_doc: naf file loaded with lxml.etree

    :rtype: dict
    :return: token index -> {'lexeme', 'lemma', 'original_pos', 'fn_pos'}
    """
    wid2lemma_pos = dict()
    for term_el in naf_doc.xpath('terms/term'):
        wid = term_el.get('id').replace('t', 'w')
        lemma = term_el.get('lemma')
        pos = term_el.get('pos')
        fn_pos = 'o'
        if pos in cat_pos2fn_pos:
            fn_pos = cat_pos2fn_pos[pos]

        wid2lemma_pos[wid] = (lemma, pos, fn_pos)

    index2info = dict()
    for index, w_el in enumerate(naf_doc.xpath('text/wf')):
        wid = w_el.get('id')
        lemma, pos, fn_pos = wid2lemma_pos[wid]
        info = {
            'lexeme': w_el.text,
            'lemma': lemma,
            'original_pos' : pos,
            'fn_pos' : fn_pos
        }
        index2info[index] = info

    return index2info

def load_token(a_token_el):
    """
    load token el into dict

    :param lxml.etree._Element a_token_el: a token element
    e.g., <token number="1" sentence="2" t_id="7">Methodes</token>

    :rtype: dict
    :return: dict containing the following keys
    ['number', 'sentence', 't_id', 'text']
    """
    token_dict = dict(a_token_el.attrib)
    token_dict['text'] = a_token_el.text

    return token_dict

token_el = etree.fromstring('<token number="1" sentence="2" t_id="7">Methodes</token>')
assert load_token(token_el) == {'number': '1', 'sentence': '2', 't_id': '7', 'text': 'Methodes'}


def load_all_tokens(the_doc, index2term_info):
    """
    loop over all 'token' elements and load them into dict

    :param lxml.etree._ElementTree the_doc: result of etree.parse('')
    :param dict index2term_info: see output load_index2term_info

    :rtype: dict
    :return: mapping t_id -> output function 'load_token'
    """
    t_id2token_info = dict()
    for index, token_el in enumerate(the_doc.xpath('token')):
        term_info = index2term_info[index]
        token_info = load_token(token_el)
        token_info['lemma'] = term_info['lemma']
        token_info['original_pos'] = term_info['original_pos']
        token_info['fn_pos'] = term_info['fn_pos']
        t_id2token_info[token_info['t_id']] = token_info

    return t_id2token_info


def load_event_mentions(the_doc, doc_name, t_id2token_info):
    """
    load all 'Markables/EVENT_MENTION' elements
    into class FRAME from module my_classes.py

    :param lxml.etree._ElementTree the_doc: result of etree.parse('')
    :param str doc_name: basename of document
    :param dict t_id2token_info: output of function 'load_all_tokens'
    :return:
    """
    m_id2event_mention_obj = dict()

    for event_mention_el in the_doc.xpath('Markables/EVENT_MENTION'):
        m_id = event_mention_el.get('m_id')
        tokens = []
        for token_anchor_el in event_mention_el.xpath('token_anchor'):
            t_id = token_anchor_el.get('t_id')
            tokens.append(t_id2token_info[t_id])

        event_mention_obj = Frame(doc_name, m_id, tokens)
        m_id2event_mention_obj[m_id] = event_mention_obj

    return m_id2event_mention_obj


def load_entity_mentions(the_doc, doc_name, t_id2token_info):
    """
    load all 'Markables/ENTITY_MENTION' elements
    into class FrameElement from module my_classes.py

    :param lxml.etree._ElementTree the_doc: result of etree.parse('')
    :param str doc_name: basename of document
    :param dict t_id2token_info: output of function 'load_all_tokens'
    :return:
    """
    m_id2entity_mention_obj = dict()

    for event_mention_el in the_doc.xpath('Markables/ENTITY_MENTION'):
        m_id = event_mention_el.get('m_id')
        tokens = []
        for token_anchor_el in event_mention_el.xpath('token_anchor'):
            t_id = token_anchor_el.get('t_id')
            tokens.append(t_id2token_info[t_id])

        event_mention_obj = FrameElement(doc_name, m_id, tokens)
        m_id2entity_mention_obj[m_id] = event_mention_obj

    return m_id2entity_mention_obj


def update_frame_and_fe_info(the_doc,
                             m_id2frame_obj,
                             m_id2frame_element_obj,
                             verbose=0):
    """
    """
    for role_el in the_doc.xpath('Relations/HAS_PARTICIPANT'):
        info = dict(role_el.attrib)

        source_id = role_el.find('source').get('m_id')
        frame_obj = m_id2frame_obj[source_id]
        target_id = role_el.find('target').get('m_id')
        frame_el_obj = m_id2frame_element_obj[target_id]

        # update Frame obj
        frame_obj.frame.add(info['frame'])

        if verbose:
            if len(frame_obj.frame) >= 2:
                print('more than one frame label for:')
                print(f"{frame_obj.doc_name} {frame_obj.m_id} {frame_obj.frame}")

        try:
            confidence_frame = info['confidence_frame']

            if info['confidence_frame']:
                try:
                    frame_obj.confidence_frame.append(int(confidence_frame))
                except ValueError:
                    frame_obj.confidence_frame.append(-1)
                    if verbose:
                        print(f'could not int: {confidence_frame}')

            else:
                frame_obj.confidence_frame.append(-1)
        except KeyError:
            frame_obj.confidence_frame.append(-1)

            if verbose:
                print('no confidence_frame key from frame el obj:')
                print(f"{frame_el_obj.doc_name} {frame_el_obj.m_id}")

        frame_obj.roles[info['frame_element']] = frame_el_obj

        # update Frame Element obj
        try:
            confidence_role = info['confidence_role']
            if confidence_role:
                try:
                    frame_el_obj.confidence_role = int(confidence_role)
                except ValueError:
                    frame_el_obj.confidence_role = -1
                    if verbose:
                        print(f'could not int: {confidence_role}')

            else:
                frame_el_obj.confidence_role = -1
        except KeyError:
            frame_el_obj.confidence_role = -1

            if verbose:
                print('no confidence_role key from frame el obj:')
                print(f"{frame_el_obj.doc_name} {frame_el_obj.m_id}")


def table(frame_label2lexeme_objs,
          frame_label2lemma_objs):

    frame_lemma_fn_pos_to_freq = defaultdict(int)

    for frame_label in frame_label2lexeme_objs:
        lemma_objs = frame_label2lemma_objs[frame_label]

        for lemma_obj in lemma_objs:
            lemma = lemma_obj.lemma
            pos = lemma_obj.pos
            frame_lemma_fn_pos_to_freq[(frame_label, lemma, pos)] += 1


    list_of_lists = []
    headers = ['Frame label', 'Lemma', 'FN pos', 'Number of annotations']

    for (frame_label, lemma, pos), freq in frame_lemma_fn_pos_to_freq.items():
        one_row = [frame_label, lemma, pos, freq]
        list_of_lists.append(one_row)

    df = pandas.DataFrame(list_of_lists, columns=headers)

    return df


def remove_and_create_folder(fldr):
    """
    Remove a folder, if existing, and re-create it.
    """
    if  os.path.exists(fldr):
        shutil.rmtree(fldr)
    os.mkdir(fldr)





