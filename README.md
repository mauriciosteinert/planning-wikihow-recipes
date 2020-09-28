# Planning WikiHow Recipes

[![DOI](https://zenodo.org/badge/299410594.svg)](https://zenodo.org/badge/latestdoi/299410594)

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

## Publication

STEINERT, Maurício; and MENEGUZZI, Felipe. Planning Domain Generation from Natural Language Step-by-Step Instructions. In 2020 Workshop on Knowledge Engineering for Planning and Scheduling (KEPS@ICAPS), Nancy, France, 2020.

```Bibtex
@inproceedings{Steinert2020,
author = {Maur\'{i}cio Steinert and Felipe Meneguzzi},
title = {{Planning Domain Generation from Natural Language Step-by-Step Instructions}},
booktitle = {Proceedings of the 2020 Workshop on Knowledge Engineering for Planning and Scheduling (KEPS@ICAPS)},
year = {2020}
}
```
