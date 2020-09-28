# Planning WikiHow Recipes

In this repository is available source code to convert natural language input into PDDL (Planning Domain Definition Language) domain description based on step-by-step instructions.

All experiments use [WikiHow Planning Recipes Dataset](https://github.com/pucrs-automated-planning/wikihow-planning-recipes-dataset).


## Requirements

View [requirements.txt](requirements.txt) for a full list of dependencies.

## Usage

run.py [-h] [--generate-wikihow-dataset] [--generate-pddl] [--wikihow-dataset-dir wikihow_dataset_dir] [--generate-wikihow-dataset-statistics] [--pddl-destination-folder pddl_destination_folder] [--solver solver]

optional arguments:
  -h, --help            show this help message and exit
  --generate-wikihow-dataset
                        Download and generate WikiHow Recipes Dataset
  --generate-pddl       Generate PDDL representation for dataset instances as specified by wikihow-dataset-dir argument
  --wikihow-dataset-dir wikihow_dataset_dir
                        Specify WikiHow Recipes Dataset directory
  --generate-wikihow-dataset-statistics
                        Generate general dataset statistics
  --pddl-destination-folder pddl_destination_folder
                        Specify generated PDDL output folder
  --solver solver       Select solver to use: rule-based | rule-based-interactive
