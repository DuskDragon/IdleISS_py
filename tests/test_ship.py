from os.path import join, dirname, abspath
from unittest import TestCase

from idleiss import ship


class HelperTestCase(TestCase):

    def test_construct_tuple(self):
        result = ship._construct_tuple(
            ship.ShipSchema, {"shield": 1, "not_shield": 1})
        self.assertEqual(result.shield, 1)
        self.assertEqual(result.armor, 0)


class FleetLibraryTestCase(TestCase):
    def setUp(self):
        pass

    def test_load_library(self):
        test_file_name = "validload.json"
        target_path = join(dirname(__file__), "data", test_file_name)
        self.library = ship.ShipLibrary(target_path)
        schema = self.library.get_ship_schemata("Small Cargo")
        self.assertEqual(schema, ship.ShipSchema("Small Cargo", "Small Cargo",
            10, 0, 200, [], 3, 1,
            ship.ShipBuffs(10, 0, 0, 0),
            ship.ShipDebuffs(0, 0, 0, 0), 2, False, False))

    def test_load_fail_incorrect_priority_target(self):
        test_file_name = "invalidpriority_target.json"
        target_path = join(dirname(__file__), "data", test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_load_fail_no_shield(self):
        test_file_name = "noshield.json"
        target_path = join(dirname(__file__), "data", test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_priority_target_refers_to_nonexistant_ship(self):
        test_file_name = "invalidpriority_target.json"
        target_path = join(dirname(__file__), "data", test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_library_structure_load(self):
        library = ship.ShipLibrary()
        library._load({
            "sizes": {
                "frigate": 35,
                "capital": 1700,
                "medium structure": 8_000,
            },
            "hullclasses": [
                "frigate",
                "cruiser",
                "battleship",
                "logistics capital",
                "dreadnaught",
                "medium structure"
            ],
            "ships": {
                "rifter": {
                    "hullclass": "frigate",
                    "shield": 391,
                    "armor": 351,
                    "hull": 336,
                    "weapons": [
                        {
                            "weapon_name": "autocannons",
                            "weapon_size": "frigate",
                            "firepower": 120,
                            "priority_targets": [
                                ["cruiser",],
                                ["battleship",],
                            ],
                        }
                    ],
                    "size": "frigate",
                    "sensor_strength": 9.6,
                },
            },
            "structures": {
                "Astrahaus": {
                    "hullclass": "medium structure",
                    "shield": 1_500_000,
                    "armor": 1_500_000,
                    "hull": 1_500_000,
                    "weapons": [
                        {
                            "weapon_name": "Standup Proximity Defense System",
                            "weapon_size": "frigate",
                            "firepower": 400,
                            "area_of_effect": 20,
                            "priority_targets": [
                                ["frigate",],
                            ],
                        },
                        {
                            "weapon_name": "Standup Anti-Capital Missile Launcher",
                            "weapon_size": "capital",
                            "firepower": 80_000,
                            "priority_targets": [
                                ["logistics capital"],
                                ["dreadnaught"],
                            ],
                        },
                    ],
                    "is_structure": True,
                    "ecm_immune": True,
                    "size": "medium structure",
                    "produces": {
                        "basic_materials": 1,
                        "advanced_materials": 0.5,
                        "money": 1,
                    },
                    "reinforce_cycles": 2,
                    "structure_tier": 0,
                    "shipyard": [],
                    "sensor_strength": 1,
                    "security": "high"
                },
            },
        })
        self.assertEqual(library.get_ship_schemata("Astrahaus").is_structure, True)


    def test_library_order(self):
        library = ship.ShipLibrary()
        library._load({
            "sizes": {
                "frigate": 35,
                "cruiser": 100,
                "battleship": 360,
                "test_structure": 1000
            },
            "hullclasses": [
                "frigate",
                "cruiser",
                "battleship",
                "test_structure"
            ],
            "ships": {
                "rifter": {
                    "hullclass": "frigate",
                    "shield": 391,
                    "armor": 351,
                    "hull": 336,
                    "weapons": [
                        {
                            "weapon_name": "autocannons",
                            "weapon_size": "frigate",
                            "firepower": 120,
                            "priority_targets": [
                                ["cruiser",],
                                ["battleship",],
                            ],
                        }
                    ],
                    "size": "frigate",
                    "sensor_strength": 9.6,
                },

                "stabber": {
                    "hullclass": "cruiser",
                    "shield": 600,
                    "armor": 1300,
                    "hull": 1300,
                    "weapons": [
                        {
                            "weapon_name": "autocannons",
                            "weapon_size": "cruiser",
                            "firepower": 330,
                            "priority_targets": [
                                ["frigate",],
                                ["battleship",],
                            ],
                        }
                    ],
                    "size": "cruiser",
                    "sensor_strength": 13,
                },

                "tempest": {
                    "hullclass": "battleship",
                    "shield": 1300,
                    "armor": 7000,
                    "hull": 6800,
                    "weapons": [
                        {
                            "weapon_name": "artillery",
                            "weapon_size": "battleship",
                            "firepower": 650,
                            "priority_targets": [
                                ["battleship",],
                                ["cruiser",],
                            ],
                        }
                    ],
                    "size": "battleship",
                    "sensor_strength": 22.4,
                },

            },
            "structures": {
                "test_starting_structure": {
                "shield": 1,
                "armor": 1,
                "hull": 1,
                "sensor_strength": 1,
                "weapons": [],
                "hullclass": "test_structure",
                "size": "test_structure",
                "structure_tier": 0,
                "reinforce_cycles": 1,
                "security": "high",
                "shipyard": [],
                "produces": {}
                }
            }
        })

        self.assertEqual([schema.name for schema in library.ordered_ship_data],
            ["rifter", "stabber", "tempest", "test_starting_structure"])
