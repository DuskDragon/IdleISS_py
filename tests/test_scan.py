from unittest import TestCase
from os.path import join, dirname

from idleiss import scan
from idleiss import ship

path_to_file = lambda fn: join(dirname(__file__), "data", fn)

class ScanTestCase(TestCase):
    def setUp(self):
        self.library = ship.ShipLibrary(path_to_file("Ships_Config.json"))

    def tearDown(self):
        pass

    def test_can_load_config(self):
        scanning = scan.Scanning(path_to_file("Scan_Config.json"), self.library)
        self.assertTrue(scanning)

    #TODO
    # def test_asDict

    #TODO
    # def test_is_scannable

    #TODO
    # def test_is_expired

    #TODO
    # def test_gen_constellation_scannables
