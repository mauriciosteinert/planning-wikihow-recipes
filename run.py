

"""
Parse input arguments
"""

import argparse
import wikiHow.WikiHow as WikiHow

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate-wikihow-dataset',
                        action='store_true',
                        help='Download and generate WikiHow Recipes Dataset')

    parser.add_argument('--generate-pddl',
                        action='store_true',
                        help='Generate PDDL representation for dataset instances as specified by wikihow-dataset-dir argument')

    parser.add_argument('--wikihow-dataset-dir',
                        help='Specify WikiHow Recipes Dataset directory')

    args = parser.parse_args()

    if args.wikihow_dataset_dir == None:
        raise Exception("You must provide --wikihow-dataset-dir information!")

    return args



def main():
    config = parseArgs()
    wikihow_dataset = WikiHow.WikiHow(config.wikihow_dataset_dir)

    entry = wikihow_dataset.get_entry(0)
    print(wikihow_dataset.process_instance(entry[1]))

    if config.generate_wikihow_dataset:
        wikihow_dataset.download()
    elif config.generate_pddl:
        gen_pddl()


if __name__ == "__main__":
    main()
