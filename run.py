
import wikiHow.WikiHow as WikiHow
import utils
import spacy

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


            print("Actions: ", actions)


    def run(self):
        if self.config.generate_wikihow_dataset:
            self.wikihow_dataset.download()
        elif self.config.generate_pddl:
            for idx, file in enumerate(self.wikihow_dataset.get_files_list()):
                # print(idx, file)
                instance = self.wikihow_dataset.process_instance(self.wikihow_dataset.get_instance(idx)[1])
                self.generate_actions(instance)
                print("--------------------------------------------------")



if __name__ == "__main__":
    app = App()
    app.run()
