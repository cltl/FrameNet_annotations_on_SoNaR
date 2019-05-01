from sonar_classes import Frame, FrameElement
from lxml import etree


def load_index2lemma_from_naf(naf_doc):
    """
    load index of token to corresponding lemma (from terms/term layer)

    :param lxml.etree._ElementTree naf_doc: naf file loaded with lxml.etree

    :rtype: dict
    :return: token index -> {'lexeme', 'lemma'}
    """
    wid2lemma = {term_el.get('id').replace('t', 'w'): term_el.get('lemma')
                 for term_el in naf_doc.xpath('terms/term')}

    index2info = dict()
    for index, w_el in enumerate(naf_doc.xpath('text/wf')):
        info = {
            'lexeme': w_el.text,
            'lemma': wid2lemma[w_el.get('id')]
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


def load_all_tokens(the_doc, index2lemma):
    """
    loop over all 'token' elements and load them into dict

    :param lxml.etree._ElementTree the_doc: result of etree.parse('')
    :param dict index2lemma: see output load_index2lemma_from_naf

    :rtype: dict
    :return: mapping t_id -> output function 'load_token'
    """
    t_id2token_info = dict()
    for index, token_el in enumerate(the_doc.xpath('token')):
        lemma = index2lemma[index]['lemma']
        token_info = load_token(token_el)
        token_info['lemma'] = lemma
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




