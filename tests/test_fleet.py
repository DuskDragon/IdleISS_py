from unittest import TestCase

from idleiss import fleet
from idleiss.ship import ShipLibrary

import random

class ShipLibraryMock(ShipLibrary):

    def __init__(self):
        self.size_data = {
            "one": 1
        }
        self.ship_data = {
            "ship1": {
                "shield": 10,
                "armor": 10,
                "hull": 100,
                "firepower": 50,
                "size": "one",
                "weapon_size": "one",
                "multishot": {
                    "ship1": 2
                }
            }
        }


class FleetTestCase(TestCase):

    def setUp(self):
        pass

    def test_build_ship(self):
        fm = fleet.FleetManager(ships={})
        fm.add_ship('ship1', 1)
        self.assertEqual(fm.ships['ship1'], 1)
