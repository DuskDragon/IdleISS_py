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
            'sizes': {
                "ship1": 1,
                "ship2": 2,
                "ship3": 3,
                "ship4": 4,
            },
            'ships': {
                "ship1": {
                    "shield": 10,
                    "armor": 10,
                    "hull": 100,
                    "firepower": 50,
                    "sensor_strength": 1,
                    "size": "ship1",
                    "weapon_size": "ship1",
                    "multishot": {
                        "ship1": 2,
                    },
                },

                "ship2": {
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "firepower": 51,
                    "sensor_strength": 1,
                    "size": "ship2",
                    "weapon_size": "ship1",
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
                    "sensor_strength": 1,
                    "size": "ship3",
                    "weapon_size": "ship1",
                    "multishot": {
                        "ship2": 25,
                    },
                },

                "ship4": {
                    "shield": 1000000,
                    "armor": 200,
                    "hull": 250000,
                    "firepower": 250000,
                    "sensor_strength": 1,
                    "size": "ship4",
                    "weapon_size": "ship1",
                    "multishot": {
                    },
                },

                "local_rep_test": {
                    "shield": 100,
                    "shield_recharge": 5,
                    "armor_local_repair": 5,
                    "armor": 100,
                    "hull": 100,
                    "firepower": 100,
                    "sensor_strength": 1,
                    "size": "ship1",
                    "weapon_size": "ship1",
                    "multishot": {
                    },
                },
                "remote_rep_test": {
                    "shield": 100,
                    "remote_shield": 10,
                    "remote_armor": 10,
                    "armor": 100,
                    "hull": 100,
                    "firepower": 100,
                    "sensor_strength": 1,
                    "size": "ship1",
                    "weapon_size": "ship1",
                    "multishot": {
                    },
                },
                "ewar_test": {
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "firepower": 100,
                    'target_painter': 0.7,
                    'tracking_disruption': 1.6,
                    'ECM': 1,
                    'web': 0.7,
                    "sensor_strength": 1,
                    "size": "ship1",
                    "weapon_size": "ship1",
                    "multishot": {
                    },
                },
                "ewar_ecm_test": {
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "firepower": 200,
                    'ECM': 1,
                    "sensor_strength": 1,
                    "size": "ship1",
                    "weapon_size": "ship1",
                    "multishot": {
                    },
                },
                "ewar_test_target": {
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "firepower": 200,
                    "sensor_strength": 0,
                    "size": "ship1",
                    "weapon_size": "ship1",
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
            Ship(schema, ShipAttributes(10, 10, 100, {})),
            Ship(schema, ShipAttributes(10, 10, 100, {})),
            Ship(schema, ShipAttributes(10, 10, 100, {})),
            Ship(schema, ShipAttributes(10, 10, 100, {})),
            Ship(schema, ShipAttributes(10, 10, 100, {})),
        ]

        result = battle.expand_fleet(ship_count, library)
        self.assertEqual(answer, result)

    def test_prune_fleet(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')

        tattered_fleet = [
            Ship(schema1, ShipAttributes(10, 5, 100, {})),
            Ship(schema1, ShipAttributes(0, 10, 100, {})),
            Ship(schema2, ShipAttributes(10, 10, 0, {})),  # how is this possible?
            Ship(schema2, ShipAttributes(10, 10, 100, {})),
            Ship(schema2, ShipAttributes(0, 0, 10, {})),
            Ship(schema3, ShipAttributes(10, 0, 10, {})),
        ]

        expected_fleet = [
            Ship(schema1, ShipAttributes(10, 5, 100, {'active': {}})),
            Ship(schema1, ShipAttributes(10, 10, 100, {'active': {}})),
            Ship(schema2, ShipAttributes(100, 10, 100, {'active': {}})),
            Ship(schema2, ShipAttributes(100, 0, 10, {'active': {}})),
            Ship(schema3, ShipAttributes(0, 0, 10, {'active': {}})),
            # balance is restored.
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
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100, {}))
        ship2 = Ship(schema1, ShipAttributes(10, 10, 0, {}))
        ship3 = Ship(schema1, ShipAttributes(10, 10, -1, {}))  # lolwut

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

    def test_true_damage_no_ewar(self):
        # weapon size less than target_size, exactly same as full damage
        self.assertEqual(battle.true_damage(100, 1, 2, {}, {}), 100)

        # weapon size at target size, ditto.
        self.assertEqual(battle.true_damage(100, 2, 2, {}, {}), 100)

        # weapon size larget than target size, 44.44% damage rounded up
        self.assertEqual(battle.true_damage(100, 3, 2, {}, {}), 45)

        # weapon size obscenely huge compared to size, still damaged.
        self.assertEqual(battle.true_damage(100, 1000, 2, {}, {}), 1)

        # weapon size just a weee bit larger than target size
        self.assertEqual(battle.true_damage(100, 10000, 9999, {}, {}), 100)

    def test_ewar_persist(self):
        library = ShipLibraryMock()
        schema_holder = library.get_ship_schemata('ship2')
        tattered_fleet = [
            Ship(schema_holder, ShipAttributes(100, 100, 100, {
                'active': {
                    'target_painter': 1,
                    'tracking_disruption': 1,
                    'ECM': 1,
                    'web': 1
                },
                'inactive': {
                    'target_painter': 2,
                    'tracking_disruption': 2,
                    'ECM': 2,
                    'web': 2
                }})),
        ]
        expected_fleet = [
            Ship(schema_holder, ShipAttributes(100, 100, 100, {
                'active': {
                    'target_painter': 2,
                    'tracking_disruption': 2,
                    'ECM': 2,
                    'web': 2
                }})),
        ]
        result = battle.prune_fleet(tattered_fleet)
        self.assertEqual(result.fleet, expected_fleet)

    def test_ewar_target_painter_effect(self):
        # make sure inactive doesn't work
        self.assertEqual(
            battle.true_damage(100, 10, 5, {}, {
                'inactive': { 'target_painter': 1 } }),
            25)
        # make sure active does
        self.assertEqual(
            battle.true_damage(100, 10, 5, {}, {
                'active': { 'target_painter': 1 } }),
            100)

    def test_ewar_tracking_disruption_effect(self):
        #make sure inactive doesn't work
        self.assertEqual(
            battle.true_damage(100, 10, 10, {
                'inactive': { 'tracking_disruption': 1 } }, {}),
            100)
        # make sure active does
        self.assertEqual(
            battle.true_damage(100, 10, 10, {
                'active': { 'tracking_disruption': 1 } }, {}),
            25)

    def test_ewar_ecm_effect(self):
        # make sure inactive doesn't prevent attacking
        library = ShipLibraryMock()
        schema3 = library.get_ship_schemata('ship3')
        # ship1 attacks ship2
        ship1 = Ship(schema3, ShipAttributes(0, 200, 200, {
            'inactive': { 'ECM': 1 }}))
        ship2 = Ship(schema3, ShipAttributes(0, 200, 200, {}))
        ship2_1 = battle.ship_attack(schema3, ship2, ship1.attributes.debuffs)
        self.assertEqual(ship2_1, Ship(schema3, ShipAttributes(0, 100, 200, {
            'active': {}, 'inactive': {}})))
        # make sure active prevents attacking
        # ship1 attacks ship2 again
        ship1 = Ship(schema3, ShipAttributes(0, 200, 200, {
            'active': { 'ECM': 1 }}))
        ship2 = Ship(schema3, ShipAttributes(0, 200, 200, {}))
        ship2_2 = battle.ship_attack(schema3, ship2, ship1.attributes.debuffs)
        self.assertEqual(ship2_2, Ship(schema3, ShipAttributes(0, 200, 200, {})))

    def test_ewar_web_effect(self):
        #make sure inactive doesn't work
        self.assertEqual(
            battle.true_damage(100, 10, 5, {}, {
                'inactive': { 'web': 1 } }),
            25)
        # make sure active does
        self.assertEqual(
            battle.true_damage(100, 10, 5, {}, {
                'active': { 'web': 1 } }),
            100)

    def test_ewar_ecm_battle(self):
        # the test target has no sensor strength
        # so it will be perma-jammed
        # on round one it will nuke off all the armor of the attacker
        # but it will not be able to make a killing blow on round 2
        # because it will be permajammed
        attacker = {
            "ewar_ecm_test": 1,
        }
        defender = {
            "ewar_test_target": 1,
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()
        schema_test = library.get_ship_schemata('ewar_ecm_test')
        schema_target = library.get_ship_schemata('ewar_test_target')

        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        self.assertEqual(battle_instance.attacker_result, {
            'ewar_ecm_test': 1,
        })
        self.assertEqual(battle_instance.defender_result, {})

    def test_ship_attack(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100, {}))
        ship2 = Ship(schema2, ShipAttributes(100, 100, 100, {}))

        random.seed(1)
        ship1_1 = battle.ship_attack(schema2, ship1, {})
        # 1 hp, below hull breach cutoff. but lucky roll, lives
        self.assertEqual(ship1_1, Ship(schema1, ShipAttributes(0, 0, 69, {
            'active': {}, 'inactive': {}})))

        ship1_2 = battle.ship_attack(schema2, ship1_1, {})
        # 1 hp, below hull breach cutoff. but roll says it dies.
        self.assertEqual(ship1_2, Ship(schema1, ShipAttributes(0, 0, 0, {
            'active': {}, 'inactive': {}})))

        ship2_1 = battle.ship_attack(schema2, ship2, {})
        self.assertEqual(ship2_1, Ship(schema2,
            ShipAttributes(49, 100, 100, {
                'active': {}, 'inactive': {}})))

        ship2_2 = battle.ship_attack(schema2, ship2_1, {})
        self.assertEqual(ship2_2, Ship(schema2,
            ShipAttributes(0, 98, 100, {
                'active': {}, 'inactive': {}})))

        ship2_2 = battle.ship_attack(schema3, ship2_2, {})
        self.assertEqual(ship2_2, Ship(schema2,
            ShipAttributes(0, 0, 98, {
                'active': {}, 'inactive': {}})))

        ship2_3 = battle.ship_attack(schema3, ship2_2, {})
        self.assertEqual(ship2_3, Ship(schema2,
            ShipAttributes(0, 0, 0, {
                'active': {}, 'inactive': {}})))

    def test_ship_attack_shield_bounce(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema4 = library.get_ship_schemata('ship4')
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100, {}))
        ship4 = Ship(schema4, ShipAttributes(1000000, 0, 50000, {}))
        ship4b = Ship(schema4, ShipAttributes(1000000, 0, 100, {}))

        random.seed(1)
        ship4_1 = battle.ship_attack(schema1, ship4, {})
        # bounced, need 13% to survive, lives with 20%
        self.assertEqual(ship4_1, Ship(schema4, ShipAttributes(
            1000000, 0, 50000, {'active': {}, 'inactive': {}})))

        # bounced, again it should be ignored.
        ship4b_1 = battle.ship_attack(schema1, ship4b, {})
        self.assertEqual(ship4b_1, Ship(schema4, ShipAttributes(
            1000000, 0, 100, {'active': {}, 'inactive': {}})))

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
            [Ship(schema1, ShipAttributes(10, 0, 70, {})),], [])
        self.assertEqual(result, [])

        # nothing attacking a fleet will still result in a round (for now?).
        result = battle.fleet_attack(
            [], [Ship(schema1, ShipAttributes(10, 0, 70, {})),])
        self.assertEqual(result.damaged_fleet,
            [Ship(schema1, ShipAttributes(10, 0, 70, {})),])

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

        self.assertEqual(attack_result.shots_taken, 8)
        self.assertEqual(attack_result.damage_taken, 340)

        result = battle.prune_fleet(attack_result.damaged_fleet)
        self.assertEqual(result.fleet, [
            Ship(schema1, ShipAttributes(10, 0, 70, {'active': {}})),
            Ship(schema1, ShipAttributes(10, 0, 70, {'active': {}})),
        ])
        self.assertEqual(result.ship_count, {
            'ship1': 2,
        })

    def test_fleet_attack_damage_limited_by_hp(self):
        attacker = {
            "ship4": 1,
        }
        defender = {
            "ship1": 1,
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        battle_instance.prepare(library)
        attack_result = battle.fleet_attack(
            battle_instance.attacker_fleet,
            battle_instance.defender_fleet,
        )

        self.assertEqual(attack_result.shots_taken, 1)
        self.assertEqual(attack_result.damage_taken, 120)

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

    def test_calculate_battle_stalemate(self):
        # too much shield and shield recharge haha.
        stalemates = {
            "ship4": 3,
        }
        rounds = 6
        battle_instance = Battle(stalemates, stalemates, rounds)
        library = ShipLibraryMock()
        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        self.assertEqual(len(battle_instance.round_results), 6)
        for a, d in battle_instance.round_results:
            self.assertEqual(a.ship_count, stalemates)
            self.assertEqual(a.shots_taken, 3)
            self.assertEqual(a.damage_taken, 750000)

            self.assertEqual(d.ship_count, stalemates)
            self.assertEqual(d.shots_taken, 3)
            self.assertEqual(d.damage_taken, 750000)

    def test_local_rep(self):
        attacker = {
            "local_rep_test": 10,
        }
        defender = {
            "local_rep_test": 20,
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()
        schema_rep = library.get_ship_schemata('local_rep_test')
        tattered_fleet = [
            Ship(schema_rep, ShipAttributes(100, 100, 100, {})),
            Ship(schema_rep, ShipAttributes(0, 0, 100, {})),
            Ship(schema_rep, ShipAttributes(10, 10, 0, {})),
            Ship(schema_rep, ShipAttributes(10, 10, 100, {})),
        ]
        expected_fleet = [
            Ship(schema_rep, ShipAttributes(100, 100, 100, {'active': {}})),
            Ship(schema_rep, ShipAttributes(5, 5, 100, {'active': {}})),
            Ship(schema_rep, ShipAttributes(15, 15, 100, {'active': {}})),
        ]
        result = battle.prune_fleet(tattered_fleet)
        self.assertEqual(result.fleet, expected_fleet)

    def test_repair_fleet(self):
        random.seed(0)
        # rep orders
        # shield: 3, 3, 1, 1, 2,
        # armor: 1, 3, 1, 1, 2
        library = ShipLibraryMock()
        schema_remote = library.get_ship_schemata('remote_rep_test')
        tattered_fleet = [
            Ship(schema_remote, ShipAttributes(100, 100, 100, {})),
            Ship(schema_remote, ShipAttributes(0, 0, 100, {})),  #0
            Ship(schema_remote, ShipAttributes(10, 10, 10, {})), #1
            Ship(schema_remote, ShipAttributes(10, 10, 0, {})),  #2
            Ship(schema_remote, ShipAttributes(99, 99, 100, {})),#3
        ]
        expected_fleet = [
            Ship(schema_remote, ShipAttributes(100, 100, 100, {})),
            Ship(schema_remote, ShipAttributes(0, 0, 100, {})),  #0
            Ship(schema_remote, ShipAttributes(30, 40, 10, {})), #1
            Ship(schema_remote, ShipAttributes(20, 20, 0, {})),  #2
            Ship(schema_remote, ShipAttributes(100, 100, 100, {})),#3
        ]
        result = battle.repair_fleet(tattered_fleet)
        self.assertEqual(result, expected_fleet)

    def test_repair_fleet_does_not_scramble(self):
        random.seed(0)
        # rep orders
        # shield: 3, 3, 1, 1, 2,
        # armor: 1, 3, 1, 1, 2
        library = ShipLibraryMock()
        schema_remote = library.get_ship_schemata('remote_rep_test')
        tattered_fleet = [
            Ship(schema_remote, ShipAttributes(0, 0, 100, {})),  #0
            Ship(schema_remote, ShipAttributes(10, 10, 10, {})), #1
            Ship(schema_remote, ShipAttributes(100, 100, 100, {})),
            Ship(schema_remote, ShipAttributes(10, 10, 0, {})),  #2
            Ship(schema_remote, ShipAttributes(99, 99, 100, {})),#3
        ]
        expected_fleet = [
            Ship(schema_remote, ShipAttributes(0, 0, 100, {})),  #0
            Ship(schema_remote, ShipAttributes(30, 40, 10, {})), #1
            Ship(schema_remote, ShipAttributes(100, 100, 100, {})),
            Ship(schema_remote, ShipAttributes(20, 20, 0, {})),  #2
            Ship(schema_remote, ShipAttributes(100, 100, 100, {})),#3
        ]
        result = battle.repair_fleet(tattered_fleet)
        self.assertEqual(result, expected_fleet)

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

        shots = [(a.shots_taken, d.shots_taken)
            for a, d in battle_instance.round_results]
        self.assertEqual(shots, [
            (185, 198),
            (73, 111),
            (22, 63),
            (2, 70),
        ])

        damage = [(a.damage_taken, d.damage_taken)
            for a, d in battle_instance.round_results]
        self.assertEqual(damage, [
            (7850, 9013),
            (3260, 4022),
            (1090, 1656),
            (100, 109),
        ])


class SimBase(object):

    def set_library(self, target_file):
        target_file = join(dirname(__file__), 'data', target_file)
        self.library = ShipLibrary(target_file)

    def fight(self, attacker, defender, seed=0, rounds=6):
        random.seed(seed)
        result = Battle(attacker, defender, rounds)
        result.prepare(self.library)
        result.calculate_battle()
        return result


class SpeedSimTestCase(TestCase, SimBase):
    """
    Based on a certain game's speedsim.

    Test result data should match as close as possible to real results.
    Note down descrepencies if no suitable seed can generate one.
    """

    def setUp(self):
        self.set_library('validgamesim.json')

    def test_battle_1(self):
        attacker = {
            'Light Fighter': 100,
        }

        defender = {
            'Light Fighter': 50,
        }

        result = self.fight(attacker, defender, 1)
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

        result = self.fight(attacker, defender, 1)
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

        result = self.fight(attacker, defender, 1)
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

        result = self.fight(attacker, defender, 27)
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

        result = self.fight(attacker, defender, 128)
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


class DucttapeSimTestCase(TestCase, SimBase):
    """
    Based on duct tape ships.
    """

    def setUp(self):
        self.set_library('og_minmatar.json')

    def test_battle_1(self):
        attacker = {
            'rifter': 1,
        }

        defender = {
            'thrasher': 1,
        }

        result = self.fight(attacker, defender, 1)
        self.assertEqual(result.attacker_fleet, [])
        self.assertEqual(len(result.round_results), 1)

        self.assertEqual(result.round_results[0][0].shots_taken, 8)
        self.assertEqual(result.round_results[0][1].ship_count, {
            'thrasher': 1,
        })

    def test_battle_2(self):
        attacker = {
            'rifter': 100,
        }

        defender = {
            'thrasher': 100,
        }

        result = self.fight(attacker, defender, 1)
        self.assertEqual(result.attacker_fleet, [])
        self.assertEqual(len(result.round_results), 1)

        self.assertEqual(result.round_results[0][0].shots_taken, 935)
        self.assertEqual(result.round_results[0][1].ship_count, {
            'thrasher': 94,
        })

    def test_battle_3(self):
        attacker = {
            'rifter': 1,
        }

        defender = {
            'tempest': 1,
        }

        result = self.fight(attacker, defender, rounds=6)
        self.assertEqual(len(result.round_results), 6)

        # first round of shots fired and damage
        self.assertEqual(result.round_results[0][0].shots_taken, 1)
        self.assertEqual(result.round_results[0][1].shots_taken, 9)
        # battleship can barely land a damage on a frigate...
        self.assertEqual(result.round_results[0][0].damage_taken, 76)
        # but who knew frigates can harass a battleship so much more.
        self.assertEqual(result.round_results[0][1].damage_taken, 3600)

        # stalemate, ofc.
        self.assertEqual(result.round_results[-1][0].ship_count, attacker)
        self.assertEqual(result.round_results[-1][1].ship_count, defender)

    def test_battle_3(self):
        attacker = {
            'rifter': 1,
            'thrasher': 1,
            'stabber': 1,
            'hurricane': 1,
            'tempest': 1,
        }

        defender = {
            'rifter': 1,
            'thrasher': 1,
            'stabber': 1,
            'hurricane': 1,
            'tempest': 1,
        }

        result = self.fight(attacker, defender, rounds=6)
        self.assertEqual(len(result.round_results), 5)

        # first round of shots fired and damage
        self.assertEqual(result.round_results[0][0].shots_taken, 10)
        self.assertEqual(result.round_results[0][1].shots_taken, 10)
        # even if same amount of shots fired, depends who got hit.
        self.assertEqual(result.round_results[0][0].damage_taken, 7228)
        self.assertEqual(result.round_results[0][1].damage_taken, 12084)
        self.assertEqual(result.round_results[0][0].ship_count, {
            'rifter': 1,
            'thrasher': 1,
            'hurricane': 1,
            'tempest': 1,
        })
        self.assertEqual(result.round_results[0][1].ship_count, {
            'rifter': 1,
            'hurricane': 1,
            'stabber': 1,
            'tempest': 1,
        })

        # I guess the hurricane did die, but not after it killed all
        # the things.
        self.assertEqual(result.round_results[-1][0].ship_count, {
            'rifter': 1,
            'tempest': 1,
        })
        self.assertEqual(result.round_results[-1][1].ship_count, {})

    def test_battle_3(self):
        attacker = {
            'hurricane': 256,
        }

        defender = {
            'stabber': 128,
            'tempest': 256,
        }

        result = self.fight(attacker, defender, rounds=6)

        # hurricanes are waaaay too OP.
        self.assertEqual(len(result.round_results), 2)
        self.assertEqual(result.round_results[0][0].ship_count, {
            'hurricane': 40,
        })
        self.assertEqual(result.round_results[0][1].ship_count, {
            'tempest': 1,
        })
        # I don't think we need to think about what happened next.
