import random

from idleiss.ship import ShipLibrary


class FleetManager(object):

    def __init__(self, ships=None):
        # ships are a dict for now.
        # keys are ship_ids (which seems to be category of ships for now)
        # and value is how many there are.
        if ships is None:
            ships = {}
        self.ships = ships

    def add_ship(self, ship_id, amount):
        self.ships[ship_id] = self.ships.get(ship_id, 0) + amount
