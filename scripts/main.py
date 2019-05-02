"""
Usage:
  main.py --annotator=<annotator> --output_folder=<output_folder>

Options:
  -h --help     Show this screen.
  --annotater=A1 | A2
  --output_folder=<output_folder> output_folder

Examples:
    python main.py --annotator=A1 --output_folder='bins'
    python main.py --annotator=A2 --output_folder='bins'

"""
import utils
import os
from pathlib import Path
from glob import glob
from lxml import etree
import pickle
from docopt import docopt


# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

annotator = arguments['--annotator']
assert annotator in {'A1', 'A2'}, f'{annotator} not an option: {"A1", "A2"}'

id2frame_obj = dict()
for path in glob(f'../corpus/{annotator}/*xml'):

    # load paths
    cat_path = Path(path)
    base = cat_path.stem.replace('-fn.txt', '')
    naf_path = Path(f'../corpus/MANUAL500-NAF/{base}.naf')
    assert cat_path.exists()
    cat_doc = etree.parse(cat_path.as_posix())
    assert naf_path.exists(), f'no equivalent for cat file {cat_path}'
    naf_doc = etree.parse(naf_path.as_posix())

    doc = etree.parse(path)
    root = doc.getroot()
    doc_name = base

    # load information about lemmatization from naf
    index2term_info = utils.load_index2term_info(naf_doc)

    t_id2token_info = utils.load_all_tokens(cat_doc, index2term_info)
    m_id2frame_obj = utils.load_event_mentions(cat_doc,
                                               doc_name,
                                               t_id2token_info)

    m_id2frame_element_obj = utils.load_entity_mentions(cat_doc,
                                                        doc_name,
                                                        t_id2token_info)
    utils.update_frame_and_fe_info(cat_doc,
                                   m_id2frame_obj,
                                   m_id2frame_element_obj,
                                   verbose=1)

    for frame_obj in m_id2frame_obj.values():
        id2frame_obj[frame_obj.id_] = frame_obj

output_folder = arguments['--output_folder']
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

output_path = os.path.join(output_folder, f'{annotator}.p')
with open(output_path, 'wb') as outfile:
    pickle.dump(id2frame_obj, outfile)
print(f'written output to: {output_path}')