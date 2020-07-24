import spacy

class RuleBased:
    def __init__(self):
        self.objects = [
            {'name': 'water', 'type': 'ingredient'},

            {'name': 'pasta', 'type': 'ingredient'},
            {'name': 'salt', 'type': 'ingredient'},
            {'name': 'sauce', 'type': 'ingredient'},
            {'name': 'noodle', 'type': 'ingredient'},

            {'name': 'pot', 'type': 'recipient'},
            {'name': 'colander', 'type': 'recipient'}
            ]

        self.actions = [
            {'name': 'fill', 'keywords': ['fill'], 'effects': [('filled', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'cover', 'keywords': ['cover'], 'effects': [('covered', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'put', 'keywords': ['put', 'add', 'toss'], 'effects': [('in', ['ingredient', 'recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'pour', 'keywords': ['pour'], 'effects': [('poured', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'stir', 'keywords': ['stir'], 'effects': [('stirred', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]},

            {'name': 'shake', 'keywords': ['shake'], 'effects': [('shaked', ['recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'recipient')]},

            {'name': 'boil', 'keywords': ['boil'], 'effects': [('boiled', ['ingredient', 'recipient'])],
            'parameters': ['ingredient', 'recipient'], 'preconditions': [('have', 'ingredient'), ('have', 'recipient')]}
        ]


    def generate(self, instance):
        # Get all recipients and ingredients on instance
        nlp = spacy.load('en_core_web_sm')
        actions_list = []
        objects_list = []
        instance_steps_list = []

        flatten = lambda l: [item for sublist in l for item in sublist]

        for sentence in instance['data']:
            print("\nSentence: {}".format(sentence))
            doc = nlp(sentence)
            actions = [action for action in self.actions for v in doc if str(v.lemma_) in action['keywords'] and str(v.dep_) == 'ROOT']

            for action in actions:
                actions_list.append(action)

            objects = [object for object in self.objects for v in doc if object['name'] == str(v.lemma_)]

            for obj in objects:
                objects_list.append(obj)
            # instance_steps_list.append({'text': sentence, 'actions': actions, 'objects': objects})

            action_preconditions_str = ""
            unsolved_preconditions_list = []

            if len(actions) > 0:
                for precondition in actions[0]['preconditions']:
                    # Find object in step that fits precondition type
                    object = [obj for obj in objects if obj['type'] == precondition[1]]

                    if len(object) > 0:
                        action_preconditions_str += "({} {}) ".format(precondition[0], object[0]['name'])
                    else:
                        # No object fits requirements, unsolved precondition
                        unsolved_preconditions_list.append(precondition)


            print("** Action: {}".format(actions))
            print("** Action preconditions: {}".format(action_preconditions_str))
            print("** Unsolved action preconditions: {}".format(unsolved_preconditions_list))

            # User interaction to manually solve pending dependencies
            if len(unsolved_preconditions_list) > 0:
                print("------------------------------------------------------------------------")
                print("----- There are some unsolved dependencies. Please provide object names to manually fill in the blanks")
                for unsolved in unsolved_preconditions_list:
                    previous_obj = [obj['name'] for obj in objects_list if obj['type'] == unsolved[1]]
                    print("Please provide a name for object type {} (previous seen objects: {})".format(unsolved[1], previous_obj))
                    # val = input()
                    # TODO check if input value is valid
                    # action_preconditions_str += "({} {}) ".format(precondition[0], str(val))
                # print("** Action preconditions: {}".format(action_preconditions_str))

        # print("***** All actions list: {}".format(actions_list))
        # print("***** All objects list: {}".format(objects_list))

        print("\n\n")
        actions_list = list({action['name']:action for action in actions_list}.values())
        objects_list = list({obj['name']:obj for obj in objects_list}.values())
        # print(objects_list)

        #
        # Generate domain file
        domain_str = "(define (domain {})\n".format(instance['name'].lower())
        domain_str += "  (:requirements :typing)\n"
        types_list = [t['type'] for t in objects_list]
        types_set = set(types_list)

        domain_str += "  (:types\n"
        for type in types_set:
            domain_str += "    {} - object\n".format(type)

        domain_str += "  )\n"

        domain_str += "  (:predicates\n"
        effects_list = []

        for action in actions_list:
            for effect in action['effects']:
                if effect[0] not in effects_list:
                    params_str = ""
                    for idx, param in enumerate(action['parameters']):
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

        # TODO
        # Goals definition
        goals_str = ""
        problem_str += "  (:goal\n"
        problem_str += "    (and {})\n".format(goals_str)
        problem_str += "  )\n"

        problem_str += ")"
        print("---------------------------------------------------")
        print(problem_str)
        print("---------------------------------------------------")
        print(domain_str)



    def solve(self, instance):
        print("Running solver ...")
        self.generate(instance)
        return None
