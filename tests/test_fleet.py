from os.path import join, dirname, abspath
from unittest import TestCase

from idleiss import fleet

class ShipTestCase(TestCase):
    pass

class FleetLibraryTestCase(TestCase):

    def setUp(self):
        pass

    def test_load_library(self):
        test_file_name = 'testlibrary1.json'
        target_path = join(dirname(__file__), test_file_name)
        self.library = fleet.ShipLibrary(target_path)

class FleetTestCase(TestCase):
    pass
