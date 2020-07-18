import argparse

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate-wikihow-dataset',
                        action='store_true',
                        help='Download and generate WikiHow Recipes Dataset')

    parser.add_argument('--generate-pddl',
                        action='store_true',
                        help='Generate PDDL representation for dataset instances as specified by wikihow-dataset-dir argument')

    parser.add_argument('--wikihow-dataset-dir',
                        metavar='wikihow_dataset_dir',
                        help='Specify WikiHow Recipes Dataset directory')

    parser.add_argument('--solver',
                        metavar='solver',
                        help='Select solver to use: rule-based | auto')

    args = parser.parse_args()

    if args.wikihow_dataset_dir == None:
        raise Exception("You must provide --wikihow-dataset-dir information!")

    return args
