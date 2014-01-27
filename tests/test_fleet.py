from unittest import TestCase

from idleiss import fleet

class LibraryStub(object):
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
                "weapon size": "one",
                "multishot": {
                    "ship1": 2
                }
            }
        }

    def ship_shield(self, name):
        return self.ship_data[name]['shield']
    def ship_armor(self, name):
        return self.ship_data[name]['armor']
    def ship_hull(self, name):
        return self.ship_data[name]['hull']
    def ship_firepower(self, name):
        return self.ship_data[name]['firepower']

class FleetTestCase(TestCase):
    pass

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
        battle_instance = fleet.Battle(attacker, defender, rounds, LibraryStub())
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
        self.assertEqual(battle_instance.expanded_attacker, exp_attack_test)
        self.assertEqual(battle_instance.expanded_defender, exp_def_test)
