import wikiHow.WikiHow as WikiHow
import utils
import solver.RuleBased as RuleBased
import solver.RuleBased2 as RuleBased2
import solver.AutoSolver as AutoSolver
import spacy
import os
import numpy as np


class App:
    def __init__(self):
        self.config = utils.parseArgs()
        self.wikihow_dataset = WikiHow.WikiHow(self.config.wikihow_dataset_dir)
        self.nlp = spacy.load('en_core_web_sm')
        self.N_GRAMS = 6

    def generate_actions(self, instance):
        print("Extracting actions ...")

        for sentence in instance:
            doc = self.nlp(sentence)
            deps = [(x, x.dep_) for x in doc]
            actions = []

            print()
            print(sentence)
            print(deps)

            for idx_deps, dep in enumerate(deps):
                if dep[1] in ('ROOT', 'conj'):
                    # Find direct object
                    end_idx = idx_deps + self.N_GRAMS if idx_deps + self.N_GRAMS < len(deps) else len(deps)
                    dobj = [x for x in deps[idx_deps + 1:end_idx] if x[1] == 'dobj']

                    if dobj:
                        obj01 = dobj[0]

                        # Check for prepositions after direct object
                        start_idx = deps.index(obj01)
                        end_idx = start_idx + self.N_GRAMS if start_idx + self.N_GRAMS < len(deps) else len(deps)
                        prep = [x for x in deps[start_idx + 1:end_idx]]

                        if prep:
                            # Try to get object after preposition
                            start_idx = deps.index(prep[0])
                            end_idx = start_idx + self.N_GRAMS if start_idx + self.N_GRAMS < len(deps) else len(deps)
                            dobj2 = [x for x in deps[start_idx + 1:end_idx] if x[1] == 'pobj']

                            if dobj2:
                                actions.append({'action': dep[0], 'object1': str(obj01[0]), 'object2': dobj2[0][0]})
                            else:
                                actions.append({'action': dep[0], 'object': str(obj01[0])})

                        else:
                            actions.append({'action': dep[0], 'object': str(obj01[0])})


            print("Actions in instruction: ", actions)


    def run(self):
        if self.config.generate_wikihow_dataset:
            self.wikihow_dataset.download()
        elif self.config.generate_wikihow_dataset_statistics:
            self.wikihow_dataset.get_statistics()
        elif self.config.generate_pddl:
            if self.config.solver == 'rule-based':
                solver = RuleBased2.RuleBased2(interactive=False, config=self.config)
            elif self.config.solver == 'rule-based-interactive':
                solver = RuleBased2.RuleBased2(interactive=True, config=self.config)
            elif self.config.solver == 'auto':
                solver = AutoSolver.AutoSolver()

            statistics = []
            total_unsolvable_problems = 0
            file_stats = os.path.join(os.path.abspath("."), "run-statistics.txt")

            for idx in range(len(self.wikihow_dataset.get_files_list())):
                instance_name, instance_data = self.wikihow_dataset.get_instance(idx)
                instance_data = self.wikihow_dataset.process_instance(instance_data)
                print("===============================================================")
                print("{} {}".format(idx, instance_name))
                res = solver.solve({'name': instance_name, 'data': instance_data})
                statistics.append([len(res['plan']), res['total_sentences'], res['total_identified_actions'], res['total_solved_actions']])

                if len(res['plan']) == 0:
                    total_unsolvable_problems += 1

            stats_mean = np.mean(statistics, axis=0)
            stats_std = np.std(statistics, axis=0)
            stats_max = np.max(statistics, axis=0)
            stats_min = np.min(statistics, axis=0)

            with open(file_stats, "w") as f:
                f.write("Total of instances: {}\n".format(len(statistics)))
                f.write("Length of plans - mean: {} - std: {} - max: {} - min: {}\n".format(stats_mean[0], stats_std[0], stats_max[0], stats_min[0]))
                f.write("Total of sentences - mean: {} - std: {} - max: {} - min: {}\n".format(stats_mean[1], stats_std[1], stats_max[1], stats_min[1]))
                f.write("Total of identified actions - mean: {} - std: {} - max: {} - min: {}\n".format(stats_mean[2], stats_std[2], stats_max[2], stats_min[2]))
                f.write("Total of solved actions - mean: {} - std: {} - max: {} - min: {}\n".format(stats_mean[3], stats_std[3], stats_max[3], stats_min[3]))
                f.write("Total of unsolvable problems (empty plans): {}\n".format(total_unsolvable_problems))



if __name__ == "__main__":
    app = App()
    app.run()
