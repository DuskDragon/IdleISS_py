from unittest import TestCase

from idleiss import fleet
from idleiss.ship import ShipLibrary

import random

class ShipLibraryMock(ShipLibrary):

    def __init__(self):
        self.size_data = {
            "one": 1
        }
        self.ship_data = {
            "ship1": {
                "shield": 10,
                "armor": 10,
                "hull": 100,
                "firepower": 50,
                "size": "one",
                "weapon_size": "one",
                "multishot": {
                    "ship1": 2
                }
            }
        }


class FleetTestCase(TestCase):

    def setUp(self):
        pass

    def test_build_ship(self):
        fm = fleet.FleetManager(ships={})
        fm.add_ship('ship1', 1)
        self.assertEqual(fm.ships['ship1'], 1)


class BattleTestCase(TestCase):

    def setUp(self):
        pass

    def test_battle_expand(self):
        attacker = {
            "ship1": 5
        }
        defender = {
            "ship1": 4
        }
        rounds = 15
        battle_instance = fleet.Battle(attacker, defender, rounds)
        exp_attack_test = {
            "ship1": [
                [10, 10, 100],
                [10, 10, 100],
                [10, 10, 100],
                [10, 10, 100],
                [10, 10, 100]
            ]
        }
        exp_def_test = {
            "ship1": [
                [10, 10, 100],
                [10, 10, 100],
                [10, 10, 100],
                [10, 10, 100]
            ]
        }
        library = ShipLibraryMock()
        battle_instance.prepare(library)
        self.assertEqual(battle_instance.attacker_fleet, exp_attack_test)
        self.assertEqual(battle_instance.defender_fleet, exp_def_test)

    def test_clean_and_restore(self):
        attacker = {
            "ship1": 5
        }
        defender = {
            "ship1": 4
        }
        rounds = 15
        battle_instance = fleet.Battle(attacker, defender, rounds)
        input_to_function = {
            "ship1": [
                [0, 5, 71],
                [0, 10, 0],
                [0, 10, 0],
                [5, 6, 80],
                [7, 10, 91]
            ]
        }
        exp_result_test = {
            "ship1": [
                [10, 5, 71],
                [10, 6, 80],
                [10, 10, 91]
            ]
        }
        library = ShipLibraryMock()
        battle_instance.prepare(library)
        result = battle_instance.\
            clean_dead_ships_restore_shields(input_to_function, library)
        self.assertEqual(exp_result_test, result)

    def test_ship_counter(self):
        attacker = {
            "ship1": 5
        }
        defender = {
            "ship1": 4
        }
        rounds = 15
        battle_instance = fleet.Battle(attacker, defender, rounds)
        input_to_function = {
            "ship1": [
                [0, 5, 10],
                [0, 10, 10],
                [0, 10, 10],
                [5, 6, 50],
                [7, 10, 10]
            ]
        }
        library = ShipLibraryMock()
        battle_instance.prepare(library)
        result = battle_instance.ship_count(input_to_function)
        self.assertEqual(result, 5)
        input2 = {
            "ship1": 10,
            "ship2": 20,
            "ship3": 30
        }
        self.assertEqual(battle_instance.ship_count(input2), 60)

    def test_clean_up_below_70_percent(self):
        random.seed(0)
        # first 5 outputs of random.random:
        # 0.8444218515250481 # survive with 16 hull or more
        # 0.7579544029403025 # survive with 24 hull or more
        # 0.420571580830845  # survive with 58 hull or more
        # 0.25891675029296335# survive with 70 hull or more (cutoff)
        # 0.5112747213686085 # survive with 49 hull or more
        attacker = {
            "ship1": 5
        }
        defender = {
            "ship1": 4
        }
        rounds = 15
        battle_instance = fleet.Battle(attacker, defender, rounds)
        input_to_function = {
            "ship1": [
                [0, 5, 50], # higher than 16 hull, survive
                [0, 10, 40],# higher than 24 hull, survive
                [0, 10, 45],# lower than 58 hull, explode
                [5, 6, 71], # higher than cutoff, survive
                [7, 10, 10] # lower than 49 hull, explode
            ]
        }
        # remember that shields are fully restored
        expected_output = {
            "ship1": [
                [10, 5, 50],
                [10, 10, 40],
                [10, 6, 71]
            ]
        }
        library = ShipLibraryMock()
        battle_instance.prepare(library)
        result = battle_instance.\
            clean_dead_ships_restore_shields(input_to_function, library)
        self.assertEqual(expected_output, result)

    def test_random_ship_selection_bad(self):
        """
        THIS TEST IS AWFUL AND NEEDS TO BE CHANGED
        """
        random.seed(1)
        # first 5 outputs of random.randint(1, 5):
        # 1
        # 5
        # 4
        # 2
        # 3
        attacker = {
            "ship1": 3
        }
        defender = {
            "ship1": 3
        }
        rounds = 15
        battle_instance = fleet.Battle(attacker, defender, rounds)
        input_to_function = {
            "ship1": [
                [0, 5, 50],
                [0, 10, 40],
                [0, 10, 45]
            ],
            "ship2": [
                [5, 6, 71],
                [7, 10, 10]
            ]
        }

        # order of this particular dictionary is 'ship2' then 'ship1' but this
        # is only valid for this exact instance of the dictionary
        self.assertEqual(battle_instance.pick_random_ship(input_to_function),
                         {'ship2': input_to_function['ship2'][0]})
        self.assertEqual(battle_instance.pick_random_ship(input_to_function),
                         {'ship1': input_to_function['ship1'][2]})
        self.assertEqual(battle_instance.pick_random_ship(input_to_function),
                         {'ship1': input_to_function['ship1'][1]})
        self.assertEqual(battle_instance.pick_random_ship(input_to_function),
                         {'ship2': input_to_function['ship2'][1]})
        self.assertEqual(battle_instance.pick_random_ship(input_to_function),
                         {'ship1': input_to_function['ship1'][0]})

    # def test_random_ship_selection_proper(self):
        # random.seed(1)
        # # first 5 outputs of random.randint(1, 5):
        # # 1
        # # 5
        # # 4
        # # 2
        # # 3
        # attacker = {
            # "ship1": 3
        # }
        # defender = {
            # "ship1": 3
        # }
        # rounds = 15
        # battle_instance = fleet.Battle(attacker, defender, rounds)
        # input_to_function = {
            # "ship1": [
                # [0, 5, 50],
                # [0, 10, 40],
                # [0, 10, 45]
            # ],
            # "ship2": [
                # [5, 6, 71],
                # [7, 10, 10]
            # ]
        # }

        # results = []
        # while len(input_to_function):
            # value = battle_instance.pick_random_ship(input_to_function)
            # self.assertRaises(ValueError, results.index(value))
            # results.append(value)
