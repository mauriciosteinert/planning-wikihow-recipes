# NLP2PDDL

In this repository is available source code to convert natural language input into PDDL (Planning Domain Definition Language) domain description.

All experiments in here uses our custom WikiHow recipes dataset. We make available in here:

* Scripts to generate WikiHow Recipes Dataset.
* Scripts to reproduce our experiments.

## How to run

To generate WikiHow Recipes Dataset

``
run.py --generate-wikihow-dataset
``

To run the experiments

``
run.py --generate-pddl --wikihow-dataset-dir <path_to_wikihow_dataset>
