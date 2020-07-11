import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import wikiHow.WikiHow as WikiHow
import unittest


class TestSuite(unittest.TestCase):
    def test_wikihow_process_instance(self):
        ground_truth_values = [
                {'instance': 'Cure-Olives',
                'data': ['obtain fresh green olives',
                'inspect the olives',
                'break the olives',
                'place the olives in a plastic bin and cover with cold water',
                'change out the water',
                'continue the process for about a week',
                'make a finish brine',
                'drain the olives and place them in a storage container',
                'cover the olives with the brine',
                'obtain fresh olives',
                'cut the olives',
                'place the olives into glass jars with lids',
                'cover the olives with a medium brine',
                'wait one week',
                'drain the olives',
                'cover the olives with a strong brine',
                'store the olives for two months',
                'obtain fully ripe olives',
                'wash the olives',
                'weigh the olives',
                'prepare a curing crate',
                'mix the olives and salt',
                'pour the mixture into a fruit crate',
                'place the crate in a covered outdoor area',
                'mix the olives after one week',
                'repeat once a week for a month',
                'strain the mixture',
                'dry the olives overnight',
                'store the olives',
                'take precautions when working with lye',
                'clean the olives',
                'place the olives in a lye-resistant container',
                'make a lye solution',
                'pour the lye over the olives',
                'stir the mixture every two hours until the lye reaches the pits',
                'switch out the lye solution if necessary',
                'soak the olives in water for two days',
                'taste test an olive on the fourth day',
                'cure the olives in a light brine']},

                {'instance': 'Cook-Pasta',
                'data': ['fill a large pot about 2/3 full of water',
                'cover the pot and bring the water to a boil',
                'add salt and 1 pound (450 g) of pasta to the boiling water',
                'set a timer for 3 to 8 minutes',
                'stir the noodles occasionally as they boil',
                "bite into a noodle to see if it's cooked enough for you",
                'scoop out about 1 cup (240 ml) of pasta water and set it aside',
                'set a colander in the sink and put on oven mitts',
                'pour the pasta into the colander and shake it',
                'avoid adding oil or running cold water over the pasta if you plan on using sauce',
                'put the pasta back into the pot and toss it with your choice of sauce',
                'toss short noodles with pesto or vegetables',
                'mix cheese into macaroni or shells to make a creamy pasta',
                'serve meaty sauce over tubular or wide pasta',
                'stir creamy alfredo sauce into long pasta']},

                {'instance': 'Cook-a-Southern-Omelet',
                'data': ["chop up any veggies or meats you'd like to add before you begin",
                'crack 3 eggs into a bowl and beat them with a fork or whisk until the color is even',
                'heat the pan empty over medium heat',
                "sauté any meats that haven't been cooked yet",
                'sauté the vegetables starting with those that need the most cooking',
                'add a bit of salt and a bit more pepper and pour in the eggs',
                'let the omelet cook for a while',
                'add any grated or sliced cheese you want',
                'flip the omelet and cook it on the other side',
                'slide the finished omelet onto a plate',
                'serve with your choice of side dishes',
                'finished']},

                {'instance': 'Cook-Zucchini',
                'data': ['finely chop the garlic clove',
                'heat olive oil in a large frying pan over medium-high heat',
                'add zucchini slices to the pan',
                'allow each side to cook until browned and then flip over and cook for another minute',
                'transfer to a dish and serve immediately',
                'preheat the oven to 425 degrees f (218 degrees c)',
                'cut the zucchini into sticks',
                'whisk the egg white and milk in a small bowl',
                'coat a baking sheet with cooking spray',
                'dip each zucchini stick into the egg white mixture first and then coat it with the breadcrumb mixture',
                'bake for 20-25 minutes',
                'remove from the oven and enjoy!',
                'preheat oven to 325 degrees f (162 degrees c)',
                'use a cheese grater to grate the zucchini',
                'mix together the flour salt baking powder baking soda and cinnamon in a large bowl',
                'beat eggs oil vanilla and sugar in a separate bowl',
                'add egg mixture to the flour mixture',
                'stir in the zucchini and nuts',
                'bake for 40-60 minutes',
                'remove from the oven',
                'serve and enjoy!']},

                {'instance': 'Cook-Arborio-Rice',
                'data': ['put arborio rice into a strainer and rinse it until the water runs clear',
                'place the rinsed rice into your rice cooker and pour in 3 cups (710 ml) of water',
                'close the lid and turn the rice cooker on',
                'fluff the arborio rice and let it sit for 10 minutes before you serve it',
                'simmer 3 cups (710 ml) of chicken broth over medium-low heat',
                'sauté 1 onion over medium-low heat for 5 to 8 minutes',
                'add the rice to the onion and cook it for 2 to 3 minutes',
                'pour the wine in the pan and let it cook off for 1 minute',
                'stir in the broth 1 ladleful at a time',
                'continue to stir in the broth and cook the rice for 18 to 22 minutes',
                'turn off the burner and stir in the butter parmesan salt and pepper',
                'preheat the oven to 325 °f (163 °c) and butter a baking dish',
                'put the rice sugar salt and optional vanilla bean into the dish',
                'pour in 4 cups (950 ml) of whole milk and scatter the butter over the top',
                'bake the pudding for 1 hour and 45 minutes and stir it frequently',
                'remove the pudding and let it sit for 10 to 15 minutes',
                'serve the arborio rice pudding with a sprinkle of cinnamon']}
        ]

        wikihow_dataset = WikiHow.WikiHow(os.path.join(os.path.dirname(__file__), 'wikihow_dataset/'))
        for idx, file in enumerate(wikihow_dataset.get_files_list()):
            ground_truth_entry = [x for x in ground_truth_values if x['instance'] == os.path.split(file)[-1]][0]

            instance_text = wikihow_dataset.get_instance(idx)[1]
            self.assertEqual(ground_truth_entry['data'], wikihow_dataset.process_instance(instance_text))






if __name__ == '__main__':
    unittest.main()
