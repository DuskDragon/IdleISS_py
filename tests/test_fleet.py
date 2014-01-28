from unittest import TestCase

from idleiss import fleet
from idleiss.ship import ShipLibrary


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
                [0, 5, 10],
                [0, 10, 0],
                [0, 10, 0],
                [5, 6, 50],
                [7, 10, 1]
            ]
        }
        exp_result_test = {
            "ship1": [
                [10, 5, 10],
                [10, 6, 50],
                [10, 10, 1]
            ]
        }
        library = ShipLibraryMock()
        battle_instance.prepare(library)
        result = battle_instance.\
            clean_dead_ships_restore_shields(input_to_function, library)
        self.assertEqual(exp_result_test, result)
