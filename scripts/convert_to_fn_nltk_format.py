"""
1. Merge FrameNet annotations on the SoNaR corpus
2. Convert frame annotations for which the annotators agree to the input format of FrameNetNLTK

Usage:
  convert_to_fn_nltk_format.py --config_path=<config_path> --verbose=<verbose>

Options:
    --config_path=<config_path>
    --verbose=<verbose> 0 --> no stdout 1 --> general stdout 2 --> detailed stdout

Example:
    python convert_to_fn_nltk_format.py --config_path="../config/v0.json" --verbose=1
"""
from docopt import docopt
import json
import os

import utils

# load arguments
arguments = docopt(__doc__)
print()
print('PROVIDED ARGUMENTS')
print(arguments)
print()

configuration = json.load(open(arguments['--config_path']))
verbose = int(arguments['--verbose'])

frame_label2lexeme_objs, \
frame_label2lemma_objs, \
merging_stats = utils.load_sonar_annotations(configuration,
                                             verbose=verbose)


df = utils.table(frame_label2lexeme_objs,
                 frame_label2lemma_objs)


utils.remove_and_create_folder(configuration['statistics_folder'])

stats_path = os.path.join(configuration['statistics_folder'],
                          'frequency.xlsx')
df.to_excel(stats_path, index=False)

