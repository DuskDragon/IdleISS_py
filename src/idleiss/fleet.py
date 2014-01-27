import random

from .ship import ShipLibrary


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


class Battle(object):

    def __init__(self, attacker, defender, rounds, *a, **kw):
        self.rounds = rounds
        # attacker and defender are dictionaries with "ship_name": number
        self.attacker = attacker
        self.defender = defender

        self.attacker_fleet = self.defender_fleet = None

    def expand(self, fleet, library):
        # for the listing of numbers of ship we need to expand to each ship
        # having it's own value for shield, armor, and hull
        # result will be returned with {"ship_type": [hparray, hparray, ...]}
        # where there are as many hparrays as there are ships
        # and hparray is: [0]=shield, [1]=armor, [2]=hull

        result = {}
        for ship_name in fleet:
            schema = library.get_ship_schemata(ship_name)
            result[ship_name] = (
                [[schema.shield, schema.armor, schema.hull]] * fleet[ship_name])
        return result

    def prepare(self, library):
        # do all the fleet preparation pre-battle using this game
        # library.
        self.attacker_fleet = self.expand(self.attacker, library)
        self.defender_fleet = self.expand(self.defender, library)

    def calculate_round(self):
        # do per-round battle here.
        pass

    def calculate_battle(self):
        # avoid using round as variable name as it's a predefined method
        # that might be useful when working with numbers.
        for r in xrange(rounds):
            results = self.calculate_round()
