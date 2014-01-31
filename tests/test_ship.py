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
            10, 0, 200, 0, 'hauler', 'fighter', {}))

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
