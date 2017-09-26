from os.path import join, dirname, abspath
from unittest import TestCase

from idleiss import ship


class HelperTestCase(TestCase):

    def test_construct_tuple(self):
        result = ship._construct_tuple(
            ship.ShipSchema, {'shield': 1, 'not_shield': 1})
        self.assertEqual(result.shield, 1)
        self.assertEqual(result.armor, 0)


class FleetLibraryTestCase(TestCase):

    def setUp(self):
        pass

    def test_load_library(self):
        test_file_name = 'validload.json'
        target_path = join(dirname(__file__), 'data', test_file_name)
        self.library = ship.ShipLibrary(target_path)
        schema = self.library.get_ship_schemata('Small Cargo')
        self.assertEqual(schema, ship.ShipSchema('Small Cargo', 'Small Cargo',
            10, 0, 200, 0, 3, 1, [], 1,
            ship.ShipBuffs(10, 0, 0, 0),
            ship.ShipDebuffs(0, 0, 0, 0)))

    def test_load_fail_incorrect_priority_target(self):
        test_file_name = 'invalidpriority_target.json'
        target_path = join(dirname(__file__), 'data', test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_load_fail_no_shield(self):
        test_file_name = 'noshield.json'
        target_path = join(dirname(__file__), 'data', test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_priority_target_refers_to_nonexistant_ship(self):
        test_file_name = 'invalidpriority_target.json'
        target_path = join(dirname(__file__), 'data', test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_library_order(self):
        library = ship.ShipLibrary()
        library._load({
            'sizes': {
                "frigate": 35,
                "cruiser": 100,
                "battleship": 360,
            },
            'hullclasses': [
                "frigate",
                "cruiser",
                "battleship"
            ],
            'ships': {
                "rifter": {
                    "hullclass": "frigate",
                    "shield": 391,
                    "armor": 351,
                    "hull": 336,
                    "firepower": 120,
                    "size": "frigate",
                    "sensor_strength": 9.6,
                    "weapon_size": "frigate",
                    "priority_targets": [
                        ["cruiser",],
                        ["battleship",],
                    ],
                },

                "stabber": {
                    "hullclass": "cruiser",
                    "shield": 600,  # 1600
                    "armor": 1300,
                    "hull": 1300,
                    "firepower": 330,
                    "size": "cruiser",
                    "sensor_strength": 13,
                    "weapon_size": "cruiser",
                    "priority_targets": [
                        ["frigate",],
                        ["battleship",],
                    ],
                },

                "tempest": {
                    "hullclass": "battleship",
                    "shield": 1300,  # 6300
                    "armor": 7000,
                    "hull": 6800,
                    "firepower": 650,
                    "size": "battleship",
                    "sensor_strength": 22.4,
                    "weapon_size": "battleship",
                    "priority_targets": [
                        ["battleship",],
                        ["cruiser",],
                    ],
                },

            },
        })

        self.assertEqual([schema.name for schema in library.ordered_ship_data],
            ['rifter', 'stabber', 'tempest'])
