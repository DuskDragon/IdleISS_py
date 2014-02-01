from unittest import TestCase
import random
from os.path import dirname, join

from idleiss import battle
from idleiss.battle import Battle

from idleiss.ship import Ship
from idleiss.ship import ShipAttributes
from idleiss.ship import ShipLibrary


class ShipLibraryMock(ShipLibrary):

    def __init__(self):
        self._load({
            'sizes': [
                "one",
                "two",
                "three",
                "four",
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
                    "size": "two",
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
                    "size": "three",
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
                    "size": "four",
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
        self.assertEqual(result.ship_count, expected_count)

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

        # attacking nothing will have no rounds.
        result = battle.fleet_attack([], [])
        self.assertEqual(result, [])

        # attacking nothing will have no rounds (for now?).
        result = battle.fleet_attack(
            [Ship(schema1, ShipAttributes(10, 0, 70)),], [])
        self.assertEqual(result, [])

        # nothing attacking a fleet will still result in a round (for now?).
        result = battle.fleet_attack(
            [], [Ship(schema1, ShipAttributes(10, 0, 70)),])
        self.assertEqual(result.damaged_fleet,
            [Ship(schema1, ShipAttributes(10, 0, 70)),])

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
        attack_result = battle.fleet_attack(
            battle_instance.attacker_fleet,
            battle_instance.defender_fleet,
        )
        result = battle.prune_fleet(attack_result.damaged_fleet)
        self.assertEqual(result.fleet, [
            Ship(schema1, ShipAttributes(10, 0, 70)),
            Ship(schema1, ShipAttributes(10, 0, 70)),
        ])
        self.assertEqual(result.ship_count, {
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

        counts = [(a.ship_count, d.ship_count)
            for a, d in battle_instance.round_results]
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


class SpeedSimTestCase(TestCase):
    """
    Based on a certain game's speedsim.

    Test result data should match as close as possible to real results.
    Note down descrepencies if no suitable seed can generate one.
    """

    def setUp(self):
        target_file = join(dirname(__file__), 'data', 'validgamesim.json')
        self.library = ShipLibrary(target_file)

    def speedsim(self, attacker, defender, seed=0):
        random.seed(seed)
        result = Battle(attacker, defender, 6)
        result.prepare(self.library)
        result.calculate_battle()
        return result

    def test_battle_1(self):
        attacker = {
            'Light Fighter': 100,
        }

        defender = {
            'Light Fighter': 50,
        }

        result = self.speedsim(attacker, defender, 1)
        self.assertEqual(result.defender_fleet, [])
        self.assertEqual(len(result.round_results), 4)

        self.assertEqual(result.round_results[-1][0].ship_count, {
            'Light Fighter': 95,
        })

    def test_battle_2(self):
        attacker = {
            'Light Fighter': 100,
            'Heavy Fighter': 60,
            'Cruiser': 40,
            'Battleship': 10,
        }

        defender = {
            'Light Fighter': 400,
            'Rocket Launcher': 50,
            'Light Laser': 10,
            'Heavy Laser': 5,
            'Gauss Cannon': 1,
        }

        result = self.speedsim(attacker, defender, 1)
        self.assertEqual(result.defender_fleet, [])
        self.assertEqual(len(result.round_results), 4)

        self.assertEqual(result.round_results[-1][0].ship_count, {
            'Light Fighter': 33,  # 33 - 35
            'Heavy Fighter': 54,  # 52 - 53
            'Cruiser': 40,        # 39 - 40
            'Battleship': 10,
        })

    def test_battle_3(self):
        attacker = {
            'Light Fighter': 2000,
            'Heavy Fighter': 500,
            'Cruiser': 1200,
            'Battleship': 300,
            'Bomber': 100,
            'Destroyer': 400,
            'Deathstar': 10,
            'Battlecruiser': 500,
        }

        defender = {
            'Light Fighter': 4000,
            'Heavy Fighter': 1000,
            'Cruiser': 200,
            'Battleship': 200,
            'Recycler': 200,
            'Bomber': 50,
            'Destroyer': 100,
            'Deathstar': 1,
            'Battlecruiser': 50,
            'Rocket Launcher': 500,
            'Light Laser': 100,
            'Heavy Laser': 60,
            'Gauss Cannon': 50,
            'Plasma Turret': 20,
            'Small Shield': 1,
            'Large Shield': 1,
        }

        result = self.speedsim(attacker, defender, 1)
        self.assertEqual(result.defender_fleet, [])
        self.assertEqual(len(result.round_results), 5)

        self.assertEqual(result.round_results[-1][0].ship_count, {
            'Light Fighter': 804,  # 752 - 782
            'Heavy Fighter': 315,   # 294 - 302
            'Cruiser': 919,        # 936 - 953
            'Battleship': 280,      # 274 - 280
            'Bomber': 99,          # 95 - 97
            'Destroyer': 378,       # 387 - 391
            'Deathstar': 10,        # 10
            'Battlecruiser': 475,   # 475 - 480
        })

        result = self.speedsim(attacker, defender, 27)
        self.assertEqual(result.defender_fleet, [])
        self.assertEqual(len(result.round_results), 5)

        self.assertEqual(result.round_results[-1][0].ship_count, {
            'Light Fighter': 782,  # 752 - 782
            'Heavy Fighter': 302,   # 294 - 302
            'Cruiser': 916,        # 936 - 953
            'Battleship': 272,      # 274 - 280
            'Bomber': 97,          # 95 - 97
            'Destroyer': 390,       # 387 - 391
            'Deathstar': 10,        # 10
            'Battlecruiser': 476,   # 475 - 480
        })

        result = self.speedsim(attacker, defender, 128)
        self.assertEqual(result.defender_fleet, [])
        self.assertEqual(len(result.round_results), 5)

        self.assertEqual(result.round_results[-1][0].ship_count, {
            'Light Fighter': 782,  # 752 - 782
            'Heavy Fighter': 308,   # 294 - 302
            'Cruiser': 946,        # 936 - 953
            'Battleship': 283,      # 274 - 280
            'Bomber': 98,          # 95 - 97
            'Destroyer': 388,       # 387 - 391
            'Deathstar': 10,        # 10
            'Battlecruiser': 477,   # 475 - 480
        })
