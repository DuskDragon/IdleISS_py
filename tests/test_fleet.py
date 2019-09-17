from unittest import TestCase

from idleiss import fleet
from idleiss.ship import ShipLibrary

import random

class ShipLibraryMock(ShipLibrary):

    def __init__(self):
        self.size_data = [
            "one"
        ]
        self.ship_data = {
            "ship1": {
                "shield": 10,
                "armor": 10,
                "hull": 100,
                "weapons": [
                    {
                        "weapon_name": "gun",
                        "weapon_size": "one",
                        "firepower": 50,
                        "priority_target": [
                            ["ship1",],
                        ],
                    },
                ],
                "sensor_strength": 1,
                "size": "one",
            },
            "structures": {
                "test_starting_structure": {
                    "structure_tier": 0
                }
            }
        }

class FleetTestCase(TestCase):

    def setUp(self):
        pass

    def test_build_ship(self):
        fm = fleet.FleetManager(ships={})
        fm.add_ship("ship1", 1)
        self.assertEqual(fm.ships["ship1"], 1)

    def test_ship_exists(self):
        fm = fleet.FleetManager(ships={})
        fm.add_ship("ship1", 1)
        self.assertEqual(fm.contains_ship("ship1"), True)
        self.assertEqual(fm.contains_ship("ship2"), False)

    def test_remove_ship(self):
        fm = fleet.FleetManager()
        self.assertEqual(fm.remove_ship("ship1", 1), False)
        fm.add_ship("ship1", 1)
        self.assertEqual(fm.remove_ship("ship1", 1), True)
        self.assertEqual(fm.contains_ship("ship1"), False)
        fm.add_ship("ship1", 1)
        self.assertEqual(fm.remove_ship("ship1", 2), False)
        fm.add_ship("ship1", 2)
        self.assertEqual(fm.remove_ship("ship1", 2), True)
        self.assertEqual(fm.ships["ship1"], 1)
