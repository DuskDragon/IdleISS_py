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
        # attacker and defender are dictionaries with "ship_type": number
        self.attacker_count = attacker
        self.defender_count = defender

        self.attacker_fleet = self.defender_fleet = None

    def ship_count(self, fleet):
        # return the number of ships in a attacker_count or defender_count
        result = 0
        for ship_type in fleet:
            result += fleet[ship_type]
        return result

    def deep_count(self, fleet):
        # return number of ships with hull above 0
        # deep_count takes the entire fleet or one ship type group in a fleet
        result = 0
        if type(fleet) is list:
            for ship in fleet:
                if ship[2] > 0:
                    result += 1
        else: # it is a dictionary
            for ship_type in fleet:
                for ship in fleet[ship_type]:
                    if ship[2] > 0:
                        result += 1
        return result

    def clean_dead_ships_restore_shields(self, fleet, library):
        # return an expanded fleet with 0 hull ships removed but with
        result = {}
        for ship_type in fleet:
            schema = library.get_ship_schemata(ship_type)
            result[ship_type] = (
                [[schema.shield, 0, 0] for i in \
                    range(self.deep_count(fleet[ship_type]))])
            processed_itr = 0
            for ship in fleet[ship_type]:
                if ship[2] > 0: # ship lived
                    result[ship_type][processed_itr][1] = ship[1]
                    result[ship_type][processed_itr][2] = ship[2]
                    processed_itr += 1
        return result

    def expand(self, fleet, library):
        # for the listing of numbers of ship we need to expand to each ship
        # having it's own value for shield, armor, and hull
        # result will be returned with {"ship_type": [hparray, hparray, ...]}
        # where there are as many hparrays as there are ships
        # and hparray is: [0]=shield, [1]=armor, [2]=hull

        result = {}
        for ship_type in fleet:
            schema = library.get_ship_schemata(ship_type)
            result[ship_type] = (
                [[schema.shield, schema.armor, schema.hull] for i in \
                    range(fleet[ship_type])])
        return result

    def prepare(self, library):
        # do all the fleet preparation pre-battle using this game
        # library.
        self.attacker_fleet = self.expand(self.attacker_count, library)
        self.defender_fleet = self.expand(self.defender_count, library)

    def calculate_round(self):
        pass
        # attacker fires and multishot is calculated on hit if a firing
        #     ship hits a target it has multishot on then the firing
        #     ship has a (multishot - 1)/multishot chance of firing.
        #     Multishot will check again on each hit on a multishot target

        # shield points are taken first (to zero, but not below)
        # armor points are taken second (to zero, but not below)
        # hull points are taken last
        # defender fires
        # ships with 70% or less hull have a 1-hull/hull_initial chance
        #     to be reduced to zero hull
        # ships with zero hull are removed
        # all shield hitpoints are restored

    def calculate_battle(self):
        # avoid using round as variable name as it's a predefined method
        # that might be useful when working with numbers.
        for r in xrange(self.rounds):
            results = self.calculate_round()
