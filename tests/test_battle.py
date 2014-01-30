from unittest import TestCase

from idleiss import battle
from idleiss.battle import Battle

from idleiss.ship import Ship
from idleiss.ship import ShipAttributes
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
                    "ship1": 2,
                },
            },

            "ship2": {
                "shield": 100,
                "armor": 100,
                "hull": 100,
                "firepower": 51,
                "size": "one",
                "weapon_size": "one",
                "multishot": {
                    "ship1": 4,
                    "ship2": 16,
                },
            },

            "ship3": {
                "shield": 0,
                "armor": 200,
                "hull": 200,
                "firepower": 100,
                "size": "one",
                "weapon_size": "one",
                "multishot": {
                    "ship2": 25,
                },
            },

        }


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
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()
        schema = library.get_ship_schemata('ship1')

        exp_attack_test = [
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
        ]

        exp_def_test = [
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
        ]
        battle_instance.prepare(library)
        self.assertEqual(battle_instance.attacker_fleet, exp_attack_test)
        self.assertEqual(battle_instance.defender_fleet, exp_def_test)

    def test_prune_fleet(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')

        tattered_fleet = [
            Ship(schema1, ShipAttributes(10, 5, 100)),
            Ship(schema1, ShipAttributes(0, 10, 100)),
            Ship(schema2, ShipAttributes(10, 10, 0)),  # how is this possible?
            Ship(schema2, ShipAttributes(10, 10, 100)),
            Ship(schema2, ShipAttributes(0, 0, 10)),
            Ship(schema3, ShipAttributes(10, 0, 10)),
        ]

        expected_fleet = [
            Ship(schema1, ShipAttributes(10, 5, 100)),
            Ship(schema1, ShipAttributes(10, 10, 100)),
            Ship(schema2, ShipAttributes(100, 10, 100)),
            Ship(schema2, ShipAttributes(100, 0, 10)),
            Ship(schema3, ShipAttributes(0, 0, 10)),  # balance is restored.
        ]

        expected_count = {
            'ship1': 2,
            'ship2': 2,
            'ship3': 1,
        }

        result = battle.prune_fleet(tattered_fleet)
        self.assertEqual(result.fleet, expected_fleet)
        self.assertEqual(result.count, expected_count)

    def test_hull_breach(self):
        random.seed(0)
        # first 5 outputs of random.random.
        # the numbers generated are hull % remaining needed to survive,
        # those over .70 always survive.

        library = ShipLibraryMock()
        schema = library.get_ship_schemata('ship1')
        # no number is rolled for this one as it is over cutoff.
        self.assertEqual(battle.hull_breach(71, 100), 71)
        self.assertEqual(battle.hull_breach(0, 100), 0) # need 84.4%
        self.assertEqual(battle.hull_breach(69, 100), 0) # ~75.8%
        self.assertEqual(battle.hull_breach(42, 100), 0) # ~42.05%
        self.assertEqual(battle.hull_breach(26, 100), 26) # ~25.89%

    def test_ship_attack(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100))
        ship2 = Ship(schema2, ShipAttributes(100, 100, 100))

        random.seed(1)
        ship1_1 = battle.ship_attack(schema2, ship1)
        # 1 hp, below hull breach cutoff. but lucky roll, lives
        self.assertEqual(ship1_1, Ship(schema1, ShipAttributes(0, 0, 69)))

        ship1_2 = battle.ship_attack(schema2, ship1_1)
        # 1 hp, below hull breach cutoff. but roll says it dies.
        self.assertEqual(ship1_2, Ship(schema1, ShipAttributes(0, 0, 0)))

        ship2_1 = battle.ship_attack(schema2, ship2)
        self.assertEqual(ship2_1, Ship(schema2,
            ShipAttributes(49, 100, 100)))

        ship2_2 = battle.ship_attack(schema2, ship2_1)
        self.assertEqual(ship2_2, Ship(schema2,
            ShipAttributes(0, 98, 100)))

        ship2_2 = battle.ship_attack(schema3, ship2_2)
        self.assertEqual(ship2_2, Ship(schema2,
            ShipAttributes(0, 0, 98)))

        ship2_3 = battle.ship_attack(schema3, ship2_2)
        self.assertEqual(ship2_3, Ship(schema2,
            ShipAttributes(0, 0, 0)))

    def test_multishot(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')
        random.seed(0)
        # schema1 can't multishoot schema2
        self.assertFalse(battle.multishot(schema1, schema2))
        # not high enough roll to go against chance.
        self.assertFalse(battle.multishot(schema1, schema1))
        # high enough roll.
        self.assertTrue(battle.multishot(schema3, schema2))

    def test_fleet_attack_empty(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        result = battle.fleet_attack([], [])
        self.assertEqual(result, [])
        result = battle.fleet_attack(
            [Ship(schema1, ShipAttributes(10, 0, 70)),], [])
        self.assertEqual(result, [])
        result = battle.fleet_attack(
            [], [Ship(schema1, ShipAttributes(10, 0, 70)),])
        self.assertEqual(result, [Ship(schema1, ShipAttributes(10, 0, 70)),])

    def test_fleet_attack(self):
        attacker = {
            "ship1": 5,
        }
        defender = {
            "ship1": 4,
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')

        random.seed(1)
        battle_instance.prepare(library)
        damaged_fleet = battle.fleet_attack(
            battle_instance.attacker_fleet,
            battle_instance.defender_fleet,
        )
        result = battle.prune_fleet(damaged_fleet)
        self.assertEqual(result.fleet, [
            Ship(schema1, ShipAttributes(10, 0, 70)),
            Ship(schema1, ShipAttributes(10, 0, 70)),
        ])
        self.assertEqual(result.count, {
            'ship1': 2,
        })

    def test_calculate_round(self):
        attacker = {
            "ship1": 15,
            "ship2": 5,
        }
        defender = {
            "ship1": 8,  # they look pretty dead.
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        random.seed(0)
        battle_instance.prepare(library)
        battle_instance.calculate_round()

        self.assertEqual(battle_instance.defender_fleet, [])

    def test_calculate_battle(self):
        attacker = {
            "ship1": 45,
            "ship2": 25,
        }
        defender = {
            "ship1": 120,  # they look pretty dead.  ship2 too stonk
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        random.seed(0)
        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        self.assertEqual(battle_instance.defender_fleet, [])
        self.assertEqual(len(battle_instance.round_results), 4)

        counts = [(a.count, d.count) for a, d in battle_instance.round_results]
        self.assertEqual(counts, [
            ({'ship1': 15, 'ship2': 23},
                {'ship1': 60}),
            ({'ship1': 4, 'ship2': 21},
                {'ship1': 21}),
            ({'ship1': 1, 'ship2': 20},
                {'ship1': 2}),
            ({'ship1': 1, 'ship2': 20},
                {}),
        ])
