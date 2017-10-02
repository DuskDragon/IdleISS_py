from unittest import TestCase
import random
from os.path import dirname, join

from idleiss import battle
from idleiss.battle import Battle
from idleiss.battle import Fleet
from idleiss.battle import AttackResult

from idleiss import ship
from idleiss.ship import Ship
from idleiss.ship import ShipDebuffs
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
                "priority_test_ship": 5,
                "priority_test_not_target": 6,
                "priority_test_target": 7
            },
            'hullclasses': [
                "generic",
                "priority_test_not_target",
                "priority_test_target"
            ],
            'ships': {
                "area_of_effect_test": {
                    "hullclass": "generic",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "aoe_test",
                            "weapon_size": "ship1",
                            "firepower": 120,
                            "priority_targets": [],
                            "area_of_effect": 3
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                    "buffs": {
                        "local_shield_repair": 10,
                    },

                },
                "ship1": {
                    "hullclass": "generic",
                    "shield": 10,
                    "armor": 10,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun1",
                            "weapon_size": "ship1",
                            "firepower": 50,
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                    "buffs": {
                        "local_shield_repair": 10,
                    },

                },

                "ship2": {
                    "hullclass": "generic",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun2",
                            "weapon_size": "ship1",
                            "firepower": 500,
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship2",
                    "buffs": {
                        "local_shield_repair": 100,
                    },

                },

                "ship3": {
                    "hullclass": "generic",
                    "shield": 0,
                    "armor": 200,
                    "hull": 200,
                    "weapons": [
                        {
                            "weapon_name": "gun3",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [
                                ["generic",],
                            ],
                        },
                    ],
                    "sensor_strength": 1,
                    "size": "ship3",
                    "buffs": {
                    },

                },

                "ship4": {
                    "hullclass": "generic",
                    "shield": 1000000, # 1,000,000
                    "armor": 200,
                    "hull": 250000, # 250,000
                    "weapons": [
                        {
                            "weapon_name": "BFG",
                            "weapon_size": "ship1",
                            "firepower": 250000, # 250,000
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship4",
                    "buffs": {
                        "local_shield_repair": 1000000, # 1,000,000
                    },
                },

                "local_rep_test": {
                    "hullclass": "local_rep_test",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                    "buffs": {
                        "local_shield_repair": 5,
                        "local_armor_repair": 5,
                    },
                },
                "remote_rep_test": {
                    "hullclass": "remote_rep_test",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                    "buffs": {
                        "remote_shield_repair": 10,
                        "remote_armor_repair": 10,
                    },
                },
                "ewar_test": {
                    "hullclass": "ewar_test",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [],
                        },
                        {
                            "weapon_name": "target_painter",
                            "weapon_size": "ship1",
                            "firepower": 0,
                            "priority_targets": [],
                            "debuffs":{
                                'target_painter': 0.7
                            }
                        },
                        {
                            "weapon_name": "tracking_disruption",
                            "weapon_size": "ship1",
                            "firepower": 0,
                            "priority_targets": [],
                            "debuffs":{
                                'tracking_disruption': 1.6
                            }
                        },
                        {
                            "weapon_name": "ECM",
                            "weapon_size": "ship1",
                            "firepower": 0,
                            "priority_targets": [],
                            "debuffs":{
                                'ECM': 1
                            }
                        },
                        {
                            "weapon_name": "web",
                            "weapon_size": "ship1",
                            "firepower": 0,
                            "priority_targets": [],
                            "debuffs":{
                                'web': 0.7
                            }
                        },
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                },
                "ewar_ecm_test": {
                    "hullclass": "ewar_ecm_test",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 200,
                            "priority_targets": [],
                        },
                        {
                            "weapon_name": "ECM",
                            "weapon_size": "ship1",
                            "firepower": 0,
                            "priority_targets": [],
                            "debuffs": {
                                'ECM': 1,
                            },
                        }
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                },
                "ewar_test_target": {
                    "hullclass": "ewar_test_target",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 200,
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 0,
                    "size": "ship1",
                },
                "ewar_test_target2": {
                    "hullclass": "ewar_test_target2",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 200,
                            "priority_targets": [],
                        }
                    ],
                    "sensor_strength": 0.1,
                    "size": "ship1",
                },
                "priority_test_ship": {
                    "hullclass": "generic",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun",
                            "weapon_size": "ship1",
                            "firepower": 300,
                            "priority_targets": [
                                ["priority_test_target",],
                                ["priority_test_not_target",],
                            ],
                        }
                    ],
                    "sensor_strength": 0.1,
                    "size": "ship1",
                },
                "priority_test_not_target": {
                    "hullclass": "priority_test_not_target",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [],
                    "sensor_strength": 0.1,
                    "size": "priority_test_not_target",
                },
                "priority_test_target": {
                    "hullclass": "priority_test_target",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [],
                    "sensor_strength": 0.1,
                    "size": "priority_test_target",
                },
                "multiple_weapon_test": {
                    "hullclass": "generic",
                    "shield": 100,
                    "armor": 100,
                    "hull": 100,
                    "weapons": [
                        {
                            "weapon_name": "gun1",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [],
                        },
                        {
                            "weapon_name": "gun2",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [],
                        },
                        {
                            "weapon_name": "gun3",
                            "weapon_size": "ship1",
                            "firepower": 100,
                            "priority_targets": [],
                        },
                    ],
                    "sensor_strength": 1,
                    "size": "ship1",
                },
            },
        })


class BattleTestCase(TestCase):

    def setUp(self):
        random.seed(0)
        pass

    def test_aoe_weapon(self):
        random.seed(0)
        library = ShipLibraryMock()
        attacker = {
            "area_of_effect_test": 1,
        }
        defender = {
            "ship1": 3,
        }

        rounds = 1
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        #round_results => [0]th round,
        #    [0]: attacker ([1]: defender)
        self.assertEqual(battle_instance.round_results[0][0].ship_count, {"area_of_effect_test":1})
        self.assertEqual(battle_instance.round_results[0][1].ship_count, {})

        self.assertEqual(battle_instance.attacker_result, {
            'area_of_effect_test': 1,
        })
        self.assertEqual(battle_instance.defender_result, {})

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
        self.assertEqual(answer, result.ships)

    def test_prune_fleet(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')

        attack_result = AttackResult([], [
            Ship(schema1, ShipAttributes(10, 5, 100)),
            Ship(schema1, ShipAttributes(0, 10, 100)),
            Ship(schema2, ShipAttributes(10, 10, 0)),  # how is this possible?
            Ship(schema2, ShipAttributes(10, 10, 100)),
            Ship(schema2, ShipAttributes(0, 0, 10)),
            Ship(schema3, ShipAttributes(10, 0, 10)),
        ], 0, 0)

        expected_fleet = [
            Ship(schema1, ShipAttributes(10, 5, 100)),
            Ship(schema1, ShipAttributes(10, 10, 100)),
            Ship(schema2, ShipAttributes(100, 10, 100)),
            Ship(schema2, ShipAttributes(100, 0, 10)),
            Ship(schema3, ShipAttributes(0, 0, 10)),
            # balance is restored.
        ]

        expected_count = {
            'ship1': 2,
            'ship2': 2,
            'ship3': 1,
        }

        result = battle.prune_fleet(attack_result)
        self.assertEqual(result.ships, expected_fleet)
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

    # XXX weapon_size vs ship_size test needed
    def test_true_damage_no_ewar(self):
        # weapon size less than target_size, exactly same as full damage
        d = ship._construct_tuple(ShipDebuffs, {})
        self.assertEqual(battle.true_damage(100, 1, 2, d, d), 100)

        # weapon size at target size, ditto.
        self.assertEqual(battle.true_damage(100, 2, 2, d, d), 100)

        # weapon size larget than target size, 44.44% damage rounded up
        self.assertEqual(battle.true_damage(100, 3, 2, d, d), 45)

        # weapon size obscenely huge compared to size, still damaged.
        self.assertEqual(battle.true_damage(100, 1000, 2, d, d), 1)

        # weapon size just a weee bit larger than target size
        self.assertEqual(battle.true_damage(100, 10000, 9999, d, d), 100)

    def test_ewar_target_painter_effect(self):
        self.assertEqual(
            battle.true_damage(100, 10, 5,
                ship._construct_tuple(ShipDebuffs, {}),
                ship._construct_tuple(ShipDebuffs, {'target_painter': 1})),
            100)

    def test_ewar_tracking_disruption_effect(self):
        self.assertEqual(
            battle.true_damage(100, 10, 10,
                ship._construct_tuple(
                    ShipDebuffs, {'tracking_disruption': 1}),
                ship._construct_tuple(ShipDebuffs, {})),
            25)

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

        #round_results => [0]th round,
        #    [0]: attacker ([1]: defender)
        self.assertEqual(battle_instance.round_results[0][0].ship_count, {"ewar_ecm_test":1})
        self.assertEqual(battle_instance.round_results[0][1].ship_count, {"ewar_test_target":1})

        self.assertEqual(battle_instance.attacker_result, {
            'ewar_ecm_test': 1,
        })
        self.assertEqual(battle_instance.defender_result, {})

    def test_ewar_ecm_battle2(self):
        # the test target has low sensor strength
        # so it will be perma-jammed
        # on round one it will nuke off all the armor of the attacker
        # but it will not be able to make a killing blow on round 2
        # because it will be permajammed
        random.seed(1)
        attacker = {
            "ewar_ecm_test": 1,
        }
        defender = {
            "ewar_test_target2": 1,
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

    def test_attackers_get_ecm(self):
        # the test target has no sensor strength
        # so it will be perma-jammed
        # on round one it will nuke off all the armor of the attacker
        # but it will not be able to make a killing blow on round 2
        # because it will be permajammed
        attacker = {
            "ewar_test_target": 1,
        }
        defender = {
            "ewar_ecm_test": 1,
        }

        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()
        schema_test = library.get_ship_schemata('ewar_ecm_test')
        schema_target = library.get_ship_schemata('ewar_test_target')

        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        #round_results => [0]th round,
        #    [0]: attacker ([1]: defender)
        self.assertEqual(battle_instance.round_results[0][0].ship_count, {"ewar_test_target":1})
        self.assertEqual(battle_instance.round_results[0][1].ship_count, {"ewar_ecm_test":1})

        self.assertEqual(battle_instance.defender_result, {
            'ewar_ecm_test': 1,
        })
        self.assertEqual(battle_instance.attacker_result, {})

    def test_ship_attack(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')
        schema2 = library.get_ship_schemata('ship2')
        schema3 = library.get_ship_schemata('ship3')
        ship1 = Ship(schema1, ShipAttributes(10, 10, 100))
        ship2 = Ship(schema2, ShipAttributes(100, 100, 100))
        ship3 = Ship(schema3, ShipAttributes(100, 100, 100))

        random.seed(1)
        #ship_attack(attacker, victim)
        ship1_1 = battle.ship_attack(ship2.schema.weapons[0], ship2.debuffs, ship1)
        self.assertEqual(ship1_1, Ship(schema1, ShipAttributes(0, 0, 0)))

        ship2_1 = battle.ship_attack(ship1.schema.weapons[0], ship1.debuffs, ship2)
        self.assertEqual(ship2_1, Ship(schema2, ShipAttributes(50, 100, 100)))

        ship2_2 = battle.ship_attack(ship1.schema.weapons[0], ship1.debuffs, ship2_1)
        self.assertEqual(ship2_2, Ship(schema2, ShipAttributes(0, 100, 100)))

    def test_fleet_attack_empty(self):
        library = ShipLibraryMock()
        schema1 = library.get_ship_schemata('ship1')

        empty_fleet = battle.expand_fleet({}, library)
        solo_fleet = battle.expand_fleet({'ship1': 1}, library)

        # attacking nothing will have no rounds.
        result = battle.fleet_attack(empty_fleet, empty_fleet, 0) # 0 is the round number
        self.assertEqual(result.damaged_fleet, empty_fleet.ships)

        # attacking nothing will have no rounds (for now?).
        result = battle.fleet_attack(solo_fleet, empty_fleet, 1) # 0 is the round number
        self.assertEqual(result.damaged_fleet, empty_fleet.ships)

        # nothing attacking a fleet will still result in a round (for now?).
        result = battle.fleet_attack(empty_fleet, solo_fleet, 2) # 0 is the round number
        self.assertEqual(result.damaged_fleet,
            [Ship(schema1, ShipAttributes(10, 10, 100)),])

    def test_size_unity_factor(self):
        self.assertEqual(battle.size_damage_factor(2,2), 1.0)

    def test_fleet_attack(self):
        # Test the result of the attacking fleet firing once on the defenders.
        # Check that the damage on the defenders is accurate to only being
        # fired on once.
        random.seed(0)
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
        result = battle.fleet_attack(
            battle_instance.attacker_fleet,
            battle_instance.defender_fleet,
            0 # round number
        )

        self.assertEqual(result.hits_taken, 5)
        self.assertEqual(result.damage_taken, 250)

        result = battle.prune_fleet(result)
        self.assertEqual(result.ships, [
            Ship(schema1, ShipAttributes(10, 0, 20)),
            Ship(schema1, ShipAttributes(10, 0, 70)),
            Ship(schema1, ShipAttributes(10, 0, 70)),
            Ship(schema1, ShipAttributes(10, 0, 70)),
        ])
        self.assertEqual(result.ship_count, {
            'ship1': 4,
        })

    def test_priority_targets(self):
        random.seed(1)
        attacker = {
            "priority_test_ship": 1,
        }
        defender = {
            "priority_test_not_target": 1,
            "priority_test_target": 1
        }
        rounds = 2
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        self.assertEqual(battle_instance.defender_fleet.ships, [])
        self.assertEqual(len(battle_instance.round_results), 2)

        counts = [(a.ship_count, d.ship_count)
            for a, d in battle_instance.round_results]
        self.assertEqual(counts, [
            ({'priority_test_ship': 1}, {'priority_test_not_target': 1}),
            ({'priority_test_ship': 1}, {})
        ])

        shots = [(a.hits_taken, d.hits_taken)
            for a, d in battle_instance.round_results]
        self.assertEqual(shots, [
            (0, 1),
            (0, 1)
        ])

        damage = [(a.damage_taken, d.damage_taken)
            for a, d in battle_instance.round_results]
        self.assertEqual(damage, [
            (0, 300),
            (0, 300)
        ])

    def test_multiple_weapons(self):
        # one ship has 3 weapons with 100 damage each
        # the other has 1 weapon with 500 damage
        # both ships should destroy each other
        random.seed(0)
        attacker = {
            "multiple_weapon_test": 1,
        }
        defender = {
            "ship2": 1,
        }
        rounds = 1
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        battle_instance.prepare(library)
        battle_instance.calculate_round(0) # round number

        self.assertEqual(battle_instance.defender_fleet.ships, [])
        self.assertEqual(battle_instance.attacker_fleet.ships, [])

    def test_fleet_attack_damage_limited_by_hp(self):
        random.seed(0)
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
            0 # round number
        )

        self.assertEqual(attack_result.hits_taken, 1)
        self.assertEqual(attack_result.damage_taken, 120)

    def test_calculate_round(self):
        random.seed(0)
        attacker = {
            "ship1": 15,
            "ship2": 1000,
        }
        defender = {
            "ship1": 8,  # they look pretty dead.
        }
        rounds = 6
        battle_instance = Battle(attacker, defender, rounds)
        library = ShipLibraryMock()

        random.seed(0)
        battle_instance.prepare(library)
        battle_instance.calculate_round(0) # round number

        self.assertEqual(battle_instance.defender_fleet.ships, [])

    def test_calculate_battle_stalemate(self):
        random.seed(0)
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
            self.assertEqual(a.hits_taken, 3)
            self.assertEqual(a.damage_taken, 750000)

            self.assertEqual(d.ship_count, stalemates)
            self.assertEqual(d.hits_taken, 3)
            self.assertEqual(d.damage_taken, 750000)

    def test_local_rep(self):
        random.seed(0)
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
        attack_result = AttackResult([], [
            Ship(schema_rep, ShipAttributes(100, 100, 100)),
            Ship(schema_rep, ShipAttributes(0, 0, 100)),
            Ship(schema_rep, ShipAttributes(10, 10, 0)),
            Ship(schema_rep, ShipAttributes(10, 10, 100)),
        ], 0, 0)
        expected_fleet = [
            Ship(schema_rep, ShipAttributes(100, 100, 100)),
            Ship(schema_rep, ShipAttributes(5, 5, 100)),
            Ship(schema_rep, ShipAttributes(15, 15, 100)),
        ]
        result = battle.prune_fleet(attack_result)
        self.assertEqual(result.ships, expected_fleet)

    def test_repair_fleet(self):
        random.seed(0)
        library = ShipLibraryMock()
        schema_remote = library.get_ship_schemata('remote_rep_test')
        tattered_fleet = [
            Ship(schema_remote, ShipAttributes(100, 100, 100)),
            Ship(schema_remote, ShipAttributes(0, 0, 100)),
            Ship(schema_remote, ShipAttributes(10, 10, 10)),
            Ship(schema_remote, ShipAttributes(10, 10, 0)),
            Ship(schema_remote, ShipAttributes(99, 99, 100)),
        ]
        expected_fleet = [
            Ship(schema_remote, ShipAttributes(100, 100, 100)),
            Ship(schema_remote, ShipAttributes(10, 0, 100)),
            Ship(schema_remote, ShipAttributes(10, 20, 10)),
            Ship(schema_remote, ShipAttributes(20, 30, 0)),
            Ship(schema_remote, ShipAttributes(100, 100, 100)),
        ]
        result = battle.repair_fleet(tattered_fleet)
        self.assertEqual(result, expected_fleet)

    def test_repair_fleet_does_not_scramble(self):
        random.seed(0)
        library = ShipLibraryMock()
        schema_remote = library.get_ship_schemata('remote_rep_test')
        tattered_fleet = [
            Ship(schema_remote, ShipAttributes(0, 0, 100)),
            Ship(schema_remote, ShipAttributes(10, 10, 10)),
            Ship(schema_remote, ShipAttributes(100, 100, 100)),
            Ship(schema_remote, ShipAttributes(10, 10, 0)),
            Ship(schema_remote, ShipAttributes(99, 99, 100)),
        ]
        expected_fleet = [
            Ship(schema_remote, ShipAttributes(10, 0, 100)),
            Ship(schema_remote, ShipAttributes(10, 20, 10)),
            Ship(schema_remote, ShipAttributes(100, 100, 100)),
            Ship(schema_remote, ShipAttributes(20, 30, 0)),
            Ship(schema_remote, ShipAttributes(100, 100, 100)),
        ]
        result = battle.repair_fleet(tattered_fleet)
        self.assertEqual(result, expected_fleet)

    def test_calculate_battle(self):
        attacker = {
            "ship2": 25,
        }
        defender = {
            "ship1": 25,  # they look pretty dead.  ship2 too stronk
        }
        max_rounds = 6
        battle_instance = Battle(attacker, defender, max_rounds)
        library = ShipLibraryMock()

        random.seed(0)
        battle_instance.prepare(library)
        battle_instance.calculate_battle()

        self.assertEqual(battle_instance.defender_fleet.ships, [])
        self.assertEqual(len(battle_instance.round_results), 2)

        counts = [(a.ship_count, d.ship_count)
            for a, d in battle_instance.round_results]
        self.assertEqual(counts, [
            ({'ship2': 25}, {'ship1': 9}),
            ({'ship2': 25}, {})
        ])

        shots = [(a.hits_taken, d.hits_taken)
            for a, d in battle_instance.round_results]
        self.assertEqual(shots, [
            (25, 25),
            (9, 25)
        ])

        damage = [(a.damage_taken, d.damage_taken)
            for a, d in battle_instance.round_results]
        self.assertEqual(damage, [
            (1250, 1920),
            (450, 1080)
        ])

    def test_generate_summary_data(self):
        pass
        #TODO: collect:
        #    shots from attackers, defenders
        #    damage dealt to/by attackers, defenders
        #    resulting ship counts for both attackers, defenders
        #    ships started with for both attackers, defenders (and ships destroyed)

    def test_generate_summary_text(self):
        pass
        #TODO: spit out a text block (with ASCII style newlines/formatting) to show summary


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
