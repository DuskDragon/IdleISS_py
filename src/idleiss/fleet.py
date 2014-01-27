import random

from .ship import ShipLibrary

class FleetManager(object):
    def __init__(self, library):
        self.library = library

class Battle(object):
    def __init__(self, attacker, defender, rounds, library):
        self.rounds = rounds
        self.library = library
        # attacker and defender are dictionaries with "ship_name": number
        self.attacker = attacker
        self.defender = defender
        self.expanded_attacker = self.expand(attacker)
        self.expanded_defender = self.expand(defender)
        #calculate_battle()

    def expand(self, fleet):
        # for the listing of numbers of ship we need to expand to each ship
        # having it's own value for shield, armor, and hull
        # result will be returned with {"ship_type": [hparray, hparray, ...]}
        # where there are as many hparrays as there are ships
        # and hparray is: [0]=shield, [1]=armor, [2]=hull
        result = {}
        for ship_name in fleet:
            result[ship_name] = [[self.library.ship_shield(ship_name), \
                                 self.library.ship_armor(ship_name), \
                                 self.library.ship_hull(ship_name)]] \
                                 *fleet[ship_name]
        return result

    def calculate_battle(self):
        pass
        # for round in xrange(rounds):
            #attacker fires first at enemy fleet
            # for

