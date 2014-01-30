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

    def test_pick_random_ship(self):
        ships = {
            "ship1": [
                [1, 2, 3],
                [4, 5, 6],
            ],
            "ship2": [
                [7, 8, 9],
            ]
        }
        battle = fleet.Battle({"ship": 1}, {"ship": 1}, 10) # Values don't matter

        # Check distribution
        dist = {}
        for i in range(100000):
            ship = battle.pick_random_ship(ships, 3)
            key = str(ship)
            if key in dist:
                dist[key] += 1
            else:
                dist[key] = 1

        for ship in sorted(dist.keys()):
            self.assertTrue(dist[ship] > 30000 and dist[ship] < 36000)

        # Ensure that method gets correct fleet_size if not supplied
        dist = {}
        for i in range(100000):
            ship = battle.pick_random_ship(ships, 3)
            key = str(ship)
            if key in dist:
                dist[key] += 1
            else:
                dist[key] = 1

        for ship in sorted(dist.keys()):
            print "%s: %i" % (ship, dist[ship])
            self.assertTrue(dist[ship] > 30000 and dist[ship] < 36000)

        # Ensure handling of out-of-bounds fleet_size
        with self.assertRaises(ValueError):
            battle.pick_random_ship({}, 1)

    def test_fire_on(self):
        random.seed(0)
        # will refire if less than 0.50 (return True)
        # first 5 outputs of random.random:
        # 0.8444218515250481 # no refire (False)
        # 0.7579544029403025 # no refire (False)
        # 0.420571580830845  # shoot again (True)
        # 0.25891675029296335# shoot again (True)
        # 0.5112747213686085 # no refire (False)
        attacker = {
            "ship1": 5
        }
        defender = {
            "ship1": 4
        }
        rounds = 15
        battle_inst = fleet.Battle(attacker, defender, rounds)
        firepower = 50
        multishot = {'ship1': 2}
        input1 = ['ship1', [51,50,50]]
        input2 = ['ship1', [25,26,50]]
        input3 = ['ship1', [10,10,50]]
        input4 = ['ship1', [0,0,0]]
        input5 = ['ship1', [0,0,1]]
        self.assertEqual(battle_inst.fire_on(input1, firepower, multishot),
                                             False)
        self.assertEqual(battle_inst.fire_on(input2, firepower, multishot),
                                             False)
        self.assertEqual(battle_inst.fire_on(input3, firepower, multishot),
                                             True)
        self.assertEqual(battle_inst.fire_on(input4, firepower, multishot),
                                             True)
        self.assertEqual(battle_inst.fire_on(input5, firepower, multishot),
                                             False)
        self.assertEqual(input1, ['ship1', [1, 50, 50]])
        self.assertEqual(input2, ['ship1', [0, 1, 50]])
        self.assertEqual(input3, ['ship1', [0, 0, 20]])
        self.assertEqual(input4, ['ship1', [0, 0, -50]])
        self.assertEqual(input5, ['ship1', [0, 0, -49]])
