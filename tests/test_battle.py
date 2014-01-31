from unittest import TestCase

from idleiss import battle
from idleiss.battle import Battle

from idleiss.ship import Ship
from idleiss.ship import ShipAttributes
from idleiss.ship import ShipLibrary

import random

class ShipLibraryMock(ShipLibrary):

    def __init__(self):
        self._load({
            'sizes': [
                "one",
            ],
            'ships': {
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

                "ship4": {
                    "shield": 1000000,
                    "armor": 200,
                    "hull": 250000,
                    "firepower": 250000,
                    "size": "one",
                    "weapon_size": "one",
                    "multishot": {
                    },
                },

            },
        })

class BattleTestCase(TestCase):

    def setUp(self):
        pass

    def test_expand_fleet(self):
        library = ShipLibraryMock()
        schema = library.get_ship_schemata('ship1')
        ship_count = {
            "ship1": 5
        }
        answer = [
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
            Ship(schema, ShipAttributes(10, 10, 100)),
        ]

        result = battle.expand_fleet(ship_count, library)
        self.assertEqual(answer, result)

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

    def test_is_alive(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100))
        ship2 = Ship(schema1, ShipAttributes(10, 10, 0))
        ship3 = Ship(schema1, ShipAttributes(10, 10, -1))  # lolwut

        self.assertTrue(battle.is_ship_alive(ship1))
        self.assertFalse(battle.is_ship_alive(ship2))
        self.assertFalse(battle.is_ship_alive(ship3))

    def test_shield_bounce(self):
        # less than default threshold, bounces off.
        self.assertEqual(battle.shield_bounce(101, 200, 1), 101)
        # not less than default threshold, punches through.
        self.assertEqual(battle.shield_bounce(99, 200, 1), 98)
        self.assertEqual(battle.shield_bounce(1, 200, 2), -1)

    def test_hull_breach(self):
        # no number is rolled for this one as it is over cutoff.
        random.seed(0)
        self.assertEqual(battle.hull_breach(72, 100, 1), 71)
        self.assertEqual(battle.hull_breach(1, 100, 1), 0) # need 84.4%
        # Doesn't matter if 0 damage, because armor or shield could have
        # taken some and send shockwave down to the weakened hull.
        # Think warp core breaches in ST:TNG.
        self.assertEqual(battle.hull_breach(69, 100, 0), 0) # ~75.8%
        self.assertEqual(battle.hull_breach(43, 100, 1), 0) # ~42.05%
        self.assertEqual(battle.hull_breach(27, 100, 1), 26) # ~25.89%

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

    def test_ship_attack_shield_bounce(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema4 = library.get_ship_schemata('ship4')
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100))
        ship4 = Ship(schema4, ShipAttributes(1000000, 0, 50000))
        ship4b = Ship(schema4, ShipAttributes(1000000, 0, 100))

        random.seed(1)
        ship4_1 = battle.ship_attack(schema1, ship4)
        # bounced, need 13% to survive, lives with 20%
        self.assertEqual(ship4_1, Ship(schema4, ShipAttributes(
            1000000, 0, 50000)))

        # bounced, again it should be ignored.
        ship4b_1 = battle.ship_attack(schema1, ship4b)
        self.assertEqual(ship4b_1, Ship(schema4, ShipAttributes(
            1000000, 0, 100)))

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
