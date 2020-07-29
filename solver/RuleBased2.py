import spacy
import os
import pyperplan

class RuleBased2:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.objects = [
            {'name': 'water', 'type': 'ingredient'},

            {'name': 'pasta', 'type': 'ingredient'},
            {'name': 'dough', 'type': 'ingredient'},
            {'name': 'salt', 'type': 'ingredient'},
            {'name': 'sauce', 'type': 'ingredient'},
            {'name': 'noodle', 'type': 'ingredient'},
            {'name': 'broccoli', 'type': 'ingredient'},
            {'name': 'floret', 'type': 'ingredient'},
            {'name': 'egg', 'type': 'ingredient'},
            {'name': 'barley', 'type': 'ingredient'},
            {'name': 'vinegar', 'type': 'ingredient'},
            {'name': 'sugar', 'type': 'ingredient'},
            {'name': 'butter', 'type': 'ingredient'},
            {'name': 'oil', 'type': 'ingredient'},
            {'name': 'cheese', 'type': 'ingredient'},
            {'name': 'flour', 'type': 'ingredient'},
            {'name': 'milk', 'type': 'ingredient'},
            {'name': 'chocolate', 'type': 'ingredient'},
            {'name': 'rice', 'type': 'ingredient'},
            {'name': 'meat', 'type': 'ingredient'},
            {'name': 'garlic', 'type': 'ingredient'},
            {'name': 'pepper', 'type': 'ingredient'},
            {'name': 'potato', 'type': 'ingredient'},
            {'name': 'bread', 'type': 'ingredient'},
            {'name': 'onion', 'type': 'ingredient'},
            {'name': 'vegetable', 'type': 'ingredient'},
            {'name': 'juice', 'type': 'ingredient'},

            {'name': 'pot', 'type': 'recipient'},
            {'name': 'colander', 'type': 'recipient'},
            {'name': 'skillet', 'type': 'recipient'},
            {'name': 'saucepan', 'type': 'recipient'},
            {'name': 'basket', 'type': 'recipient'},
            {'name': 'bowl', 'type': 'recipient'}
            ]

        self.actions = [
            {'name': 'heat', 'keywords': ['heat'], 'effects': [('heated', ['ingredient', 'recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'clean', 'keywords': ['clean'], 'effects': [('cleaned', ['ingredient'])],
            'parameters': ['ingredient'], 'preconditions': [('have', 'ingredient')]},

            {'name': 'cook', 'keywords': ['cook', 'steam', 'bake'], 'effects': [('cooked', ['ingredient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'cut', 'keywords': ['cut', 'slice'], 'effects': [('cutted', ['ingredient'])],
            'parameters': ['ingredient'], 'preconditions': [('have', 'ingredient')]},

            {'name': 'cover', 'keywords': ['cover'], 'effects': [('covered', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'recipient')]},

            {'name': 'put', 'keywords': ['put', 'add', 'fill', 'toss', 'place', 'beat', 'sprinkle', 'mix'], 'effects': [('in', ['ingredient', 'recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'pour', 'keywords': ['pour', 'drain'], 'effects': [('poured', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'stir', 'keywords': ['stir'], 'effects': [('stirred', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'shake', 'keywords': ['shake'], 'effects': [('shaked', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'recipient')]},

            {'name': 'boil', 'keywords': ['boil'], 'effects': [('boiled', ['ingredient', 'recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]}
        ]


    def solve(self, instance):
        actions_list = []
        objects_list = []
        goals_list = []

        total_identified_actions = 0

        domain_file = os.path.join("./pddl/", instance['name'].lower() + "-domain.pddl")
        problem_file = os.path.join("./pddl/", instance['name'].lower() + "-problem.pddl")
        plan_file = os.path.join("./pddl/", instance['name'].lower() + "-plan.txt")

        for sentence in instance['data']:
            # print(sentence)
            doc = self.nlp(sentence)

            # Extract actions and objects in sentence
            actions = [action for action in self.actions for word in doc if str(word.lemma_) in action['keywords'] and str(word.dep_) == 'ROOT']
            objects = [obj for obj in self.objects for word in doc if obj['name'] == str(word.lemma_)]

            total_identified_actions += len(actions)

            for obj in objects:
                objects_list.append(obj)
            #
            # Select actions' effects which sentences satisfies actions parameters
            for action in actions:
                effect_objects_str = ""
                for action_parameter in action['parameters']:
                    object = next((obj for obj in objects if obj['type'] == action_parameter), None)

                    if object != None:
                        effect_objects_str += "{} ".format(object['name'])
                    else:
                        break

                if object != None:
                    for action in actions:
                        actions_list.append(action)

                    for effect in action['effects']:
                        effect_params_str = ""
                        for effect_param in effect[1]:
                            obj = next((obj['name'] for obj in objects if obj['type'] == effect_param), None)
                            effect_params_str += "{} ".format(obj)

                        goals_list.append("({} {}) ".format(effect[0], effect_params_str))

            print("\n\nSentence: {}".format(sentence))
            print("Actions: {}".format(actions))
            print("Objects: {}".format(objects))


        # Eliminate duplicated actions and objects
        actions_list = list({action['name']:action for action in actions_list}.values())
        objects_list = list({obj['name']:obj for obj in objects_list}.values())


        # Generate domain file
        with open(domain_file, "w") as f:
            # Generate actions' effects string list to fill in predicates and actions effects
            actions_params_list = []

            for action in actions_list:
                actions_effects_str_list = []
                for action_effect in action['effects']:

                    effect_parameters_str = ""
                    pred_params_str = ""
                    param_idx = None

                    for effect_param in action_effect[1]:
                        try:
                            param_idx = action['parameters'].index(effect_param)
                        except ValueError:
                            param_idx = None
                            break

                        if param_idx != None:
                            effect_parameters_str += ("?param{} ".format(param_idx))
                            pred_params_str += ("?param{} - {} ".format(param_idx, effect_param))

                    if param_idx == None:
                        # Ignore current effect
                        continue

                    actions_effects_str_list.append((action_effect[0], effect_parameters_str, pred_params_str))

                actions_params_list.append({'name': action['name'], 'parameters': action['parameters'], 'effect_parameters': actions_effects_str_list})

            f.write("(define (domain {})\n".format(instance['name'].lower()))
            f.write("  (:requirements :typing)\n")
            f.write("  (:types\n    ingredient recipient - object\n  )\n")


            # Predicates
            f.write("  (:predicates\n")
            # Static entry - mandatory for all actions
            f.write("    (have ?param - object)\n")

            for entry in actions_params_list:
                for predicate in entry['effect_parameters']:
                    f.write("    ({} {})\n".format(predicate[0], predicate[2]))
            f.write("  )\n")

            # Actions
            for entry_idx, entry in enumerate(actions_params_list):
                f.write("  (:action {}\n".format(entry['name']))

                f.write("    :parameters (")
                for parameter_idx, parameter in enumerate(entry['parameters']):
                    f.write("?param{} - {} ".format(parameter_idx, parameter))
                f.write(")\n")

                # Get effects from all previous seen actions
                previous_actions_effects_str = ""

                for previous_action in actions_params_list[:entry_idx]:
                    for action_effect in previous_action['effect_parameters']:
                        previous_actions_effects_str += "({} {}) ".format(action_effect[0], action_effect[1])

                f.write("    :precondition (and {})\n".format(previous_actions_effects_str))

                # Actions effects
                action_effects_str = ""
                for action_effect in entry['effect_parameters']:
                    action_effects_str += "({} {})".format(action_effect[0], action_effect[1])

                f.write("    :effect (and {})\n".format(action_effects_str))
                f.write("  )\n")

            f.write(")\n")


            # Problem file
            with open(problem_file, "w") as f:
                f.write("(define (problem {}-problem)\n".format(instance['name'].lower()))
                f.write("  (:domain {})\n".format(instance['name'].lower()))

                f.write("  (:objects\n")
                for object in objects_list:
                    f.write("    {} - {}\n".format(object['name'], object['type']))
                f.write("  )\n")

                f.write("  (:init\n    ")
                for object in objects_list:
                    f.write("(have {}) ".format(object['name']))
                f.write("\n  )\n")

                f.write("  (:goal\n    (and ")
                for goal in goals_list:
                    f.write("    {}\n".format(goal))
                f.write(")\n  )\n")

                f.write(")")


        # Try to devise a plan for described domain and problem
        plan = pyperplan.search_plan(domain_file, problem_file, pyperplan.SEARCHES['bfs'], None)

        if plan == None:
            plan = []
        else:
            with open(plan_file, "w") as f:
                for entry in plan:
                    f.write(str(entry))


        return {'plan': plan,
                'total_sentences': len(instance['data']),
                'total_identified_actions': total_identified_actions,
                'total_solved_actions': len(actions_list)}
