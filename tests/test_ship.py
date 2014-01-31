from os.path import join, dirname, abspath
from unittest import TestCase

from idleiss import ship


class FleetLibraryTestCase(TestCase):

    def setUp(self):
        pass

    def test_load_library(self):
        test_file_name = 'ShipLibrary Test Files/validload.json'
        target_path = join(dirname(__file__), test_file_name)
        self.library = ship.ShipLibrary(target_path)
        schema = self.library.get_ship_schemata('small hauler')
        self.assertEqual(schema, ship.ShipSchema('small hauler',
            10, 0, 200, 0, 3, 0, {}))

    def test_load_fail_no_shield(self):
        test_file_name = 'ShipLibrary Test Files/noshield.json'
        target_path = join(dirname(__file__), test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_multishot_refers_to_nonexistant_ship(self):
        test_file_name = 'ShipLibrary Test Files/invalidmultishot.json'
        target_path = join(dirname(__file__), test_file_name)
        with self.assertRaises(ValueError) as context:
            self.library = ship.ShipLibrary(target_path)

    def test_library_order(self):
        library = ship.ShipLibrary()
        library._load({
            'sizes': [
                "frigate",
                "cruiser",
                "battleship",
            ],

            'ships': {
                "rifter": {
                    "shield": 391,
                    "armor": 351,
                    "hull": 336,
                    "firepower": 120,
                    "size": "frigate",
                    "weapon_size": "frigate",
                    "multishot": {
                        "stabber": 3,
                        "tempest": 30,
                    },
                },

                "stabber": {
                    "shield": 600,  # 1600
                    "armor": 1300,
                    "hull": 1300,
                    "firepower": 330,
                    "size": "cruiser",
                    "weapon_size": "cruiser",
                    "multishot": {
                        "rifter": 9,
                        "tempest": 10,
                    },
                },

                "tempest": {
                    "shield": 1300,  # 6300
                    "armor": 7000,
                    "hull": 6800,
                    "firepower": 650,
                    "size": "battleship",
                    "weapon_size": "battleship",
                    "multishot": {
                        "stabber": 25,
                        "tempest": 2,
                    },
                },

            },
        })

        self.assertEqual([schema.name for schema in library.ordered_ship_data],
            ['rifter', 'stabber', 'tempest'])
