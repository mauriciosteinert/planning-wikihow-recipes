import spacy
import os
import pyperplan

class RuleBased:
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
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient')]},

            {'name': 'cook', 'keywords': ['cook', 'steam', 'bake'], 'effects': [('cooked', ['ingredient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'cut', 'keywords': ['cut', 'slice'], 'effects': [('cutted', ['ingredient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient')]},

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


    def generate(self, instance):
        total_discarded_actions = 0
        total_detected_actions = 0

        # Get all recipients and ingredients on instance

        actions_list = []
        objects_list = []
        instance_steps_list = []
        goals_str = ""

        flatten = lambda l: [item for sublist in l for item in sublist]

        for sentence in instance['data']:
            doc = self.nlp(sentence)
            actions = [action for action in self.actions for v in doc if str(v.lemma_) in action['keywords'] and str(v.dep_) == 'ROOT']
            objects = [object for object in self.objects for v in doc if object['name'] == str(v.lemma_)]

            total_detected_actions += len(actions)

            for obj in objects:
                objects_list.append(obj)

            for action in actions:
                actions_list.append(action)

            action_preconditions_str = ""
            unsolved_preconditions_list = []

            if len(actions) > 0:
                action_params_list = []
                for precondition in actions[0]['preconditions']:
                    # Find object in step that fits precondition type
                    object = [obj for obj in objects if obj['type'] == precondition[1]]

                    if len(object) > 0:
                        action_params_list.append(object)
                        action_preconditions_str += "({} {}) ".format(precondition[0], object[0]['name'])
                    else:
                        # No object fits requirements, unsolved precondition
                        unsolved_preconditions_list.append(precondition)

                # Process effect parameters to include into goal
                if len(unsolved_preconditions_list) == 0:
                    params_str = ""
                    params_list = [p1 for p1 in action_params_list for p2 in actions[0]['effects'][0][1] if p1[0]['type'] == p2]

                    for p in params_list:
                        params_str += "{} ".format(p[0]['name'])

                    goals_str += "({} {}) ".format(actions[0]['effects'][0][0], params_str)
                else:
                    total_discarded_actions += 1

            # print("** Action: {}".format(actions))
            # print("** Action preconditions: {}".format(action_preconditions_str))
            # print("** Unsolved action preconditions: {}".format(unsolved_preconditions_list))

        #
        actions_list = list({action['name']:action for action in actions_list}.values())
        objects_list = list({obj['name']:obj for obj in objects_list}.values())

        #
        # Generate domain file
        domain_str = "(define (domain {})\n".format(instance['name'].lower())
        domain_str += "  (:requirements :typing)\n"
        types_list = [t['type'] for t in objects_list]
        types_set = set(types_list)

        domain_str += "  (:types\n"
        domain_str += "    ingredient recipient - object"
        # for type in types_set:
        #     domain_str += "    {} - object\n".format(type)

        domain_str += "  )\n"

        domain_str += "  (:predicates\n"
        domain_str += "    (have ?param - object)\n"
        effects_list = []

        for action in actions_list:
            for effect in action['effects']:
                if effect[0] not in effects_list:
                    params_str = ""
                    for idx, param in enumerate(effect[1]):
                        params_str += "?param{} - {} ".format(idx, param)
                    domain_str += "    ({} {})\n".format(effect[0], params_str)

        domain_str += "  )\n"

        # Actions
        for curr_action_idx, action in enumerate(actions_list):
            domain_str += "  (:action {}\n".format(action['name'])
            params_str = ""
            params_list = []

            for idx, param in enumerate(action['parameters']):
                params_list.append(('param{}'.format(idx), param))
                params_str += "?param{} - {} ".format(idx, param)

            domain_str += "    :parameters ({})\n".format(params_str)

            preconditions_str = ""
            for precondition in action['preconditions']:
                param_ef = [p for p in params_list if p[1] == precondition[1]]

                if len(param_ef) > 0:
                    preconditions_str += "({} ?{}) ".format(precondition[0], param_ef[0][0])

            # Add previous action effects as preconditions for current action
            previous_action_effects_str = ""
            for previous_action in actions_list[:curr_action_idx]:
                for previous_effect in previous_action['effects']:
                    previous_params_str = ""
                    for previous_param in previous_effect[1]:
                        p = [p for p in params_list if p[1] == previous_param]

                        if len(p) > 0:
                            previous_params_str += "?{} ".format(p[0][0])

                previous_action_effects_str += "({} {}) ".format(previous_effect[0], previous_params_str)

            domain_str += "    :precondition (and {} {})\n".format(preconditions_str, previous_action_effects_str)

            effects_str = ""
            for effect in action['effects']:
                # Find parameter of same effects' type
                params_str = ""
                for param in effect[1]:
                    p = [p for p in params_list if p[1] == param]

                    if len(p) > 0:
                        params_str += "?{} ".format(p[0][0])

                effects_str += "({} {}) ".format(effect[0], params_str)

            domain_str += "    :effect (and {})\n".format(effects_str)

            domain_str += "  )\n"

        domain_str += ")\n"

        #
        # Generate problem file
        problem_str = "(define (problem {})\n".format(instance['name'].lower())
        problem_str +=   "(:domain {})\n".format(instance['name'].lower())
        # Objects and type definition
        problem_str += "  (:objects\n"

        init_have_objects_str = ""

        for object in objects_list:
            problem_str += "    {} - {}\n".format(object['name'], object['type'])
            # Generate 'have' facts for all objects
            init_have_objects_str += "(have {}) ".format(object['name'])

        problem_str += "  )\n"

        # Init parameters
        problem_str += "  (:init\n"
        problem_str += "    {}\n".format(init_have_objects_str)
        problem_str += "  )\n"

        problem_str += "  (:goal\n"
        problem_str += "    (and {})\n".format(goals_str)
        problem_str += "  )\n"

        problem_str += ")"
        #


        # print("---------------------------------------------------")
        # print(problem_str)
        # print("---------------------------------------------------")
        # print(domain_str)
        # Write domain and problem PDDL files
        domain_file = os.path.join('./pddl', instance['name'].lower() + "-domain.pddl")
        problem_file = os.path.join('./pddl', instance['name'].lower() + "-problem.pddl")
        solution_file = os.path.join('./pddl', instance['name'].lower() + "-problem-solution.txt")

        with open(domain_file, "w") as f:
            f.write(domain_str)
        with open(problem_file, "w") as f:
            f.write(problem_str)

        plan = pyperplan.search_plan(domain_file, problem_file, pyperplan.SEARCHES['gbf'], pyperplan.HEURISTICS['blind'])

        if plan == None:
            plan = []
        else:
            with open(solution_file, "w") as f:
                for line in plan:
                    f.write(str(line))

        return len(instance['data']), total_detected_actions, total_discarded_actions, len(plan)


    def solve(self, instance):
        print("Running solver ...")
        return self.generate(instance)
