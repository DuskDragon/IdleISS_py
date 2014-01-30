import random

from idleiss.ship import ShipLibrary


class Battle(object):

    def __init__(self, attacker, defender, rounds, *a, **kw):
        self.rounds = rounds
        # attacker and defender are dictionaries with "ship_type": number
        self.attacker_count = attacker
        self.defender_count = defender

        self.attacker_fleet = self.defender_fleet = None

    def ship_count(self, fleet):
        # this returns the number of ships in attacker_count or defender_count
        result = 0
        if type(fleet.values()[0]) is int: # simple count
            for ship_type in fleet:
                result += fleet[ship_type]
            return result
        else: # expanded "fleet"
            for ship_type in fleet:
                result += len(fleet[ship_type])
        return result

    def has_ships(self, fleet):
        if type(fleet.values()[0]) is int: # simple fleet
            for ship_type in fleet:
                if fleet[ship_type] > 0:
                    return True
        else: # expanded "fleet"
            for ship_type in fleet:
                if len(fleet[ship_type]) > 0:
                    return True
        return False

    def explode(self, hull, max_hull):
        # only send full, expanded fleets to this function
        # ships at 70% hull or lower will have a chance at exploding
        # chance = 1-hull/hull_initial
        if (float(hull) / float(max_hull)) < 0.70: # danger range
            chance = 1.0 - (float(hull)/float(max_hull))
            if chance < random.random():
                return hull # it lives
            else:
                return 0 # it explodes
        else: # not in danger range
            return hull

    def pick_random_ship(self, fleet, fleet_size): #trying without using fleet_size=None
        """ Battle.pick_random_ship(fleet, fleet_size) => {ship_type: hp_array} """
        # if fleet_size is None:
        #     fleet_size = self.ship_count(fleet)

        ship_idx = random.randint(1, fleet_size)
        ship_types = fleet.keys()

        for ship_type in ship_types:
            type_count = len(fleet[ship_type])
            if type_count < ship_idx:
                ship_idx -= type_count
            else:
                return [ship_type, fleet[ship_type][ship_idx - 1]]

        raise ValueError('fleet has less than fleet_size (%i) ships' % fleet_size)

    def clean_dead_ships_restore_shields(self, fleet, library):
        # return an expanded fleet with 0 hull ships removed but with
        # shields recharged and armor/hull damage persisting
        result = {}
        for ship_type in fleet:
            schema = library.get_ship_schemata(ship_type)
            # Recharge the shield by taking the full shield value from
            # the schema for this ship type, and persist the current
            # armor and hull value if the ship is not destroyed, as
            # defined by having a hull value (element [2]) of greater
            # than 0. The explode check is also calculated here.
            # if ships are actually of the ShipSchema namedtuple, access
            # by attribute id can be done instead.
            result[ship_type] = [[schema.shield, ship[1], ship[2]]
                for ship in fleet[ship_type] \
                    if self.explode(ship[2], schema.hull) > 0]
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

    def fire_on(self, ship, firepower, multishot):
        # ship[0] = ship_type
        # ship[1] = hparray -> [shield, armor, hull]
        if ship[1][0] >= firepower: # if current shields are >= firepower
            ship[1][0] -= firepower
        else: #shields are overwelmed
            remaining_firepower = firepower - ship[1][0]
            ship[1][0] = 0
            if ship[1][1] >= remaining_firepower: # if current armor is >= firepower
                ship[1][1] -= remaining_firepower
            else: # armor is overwhelmed
                remaining_firepower -= ship[1][1]
                ship[1][1] = 0
                ship[1][2] -= remaining_firepower # strikes hull
        # now return if multishot is true
        if ship[0] in multishot: # check if chance of multishot
            chance = (multishot[ship[0]] - 1.0) / multishot[ship[0]]
            if chance > random.random():
                return True # extra shot -> fire again
            else:
                return False # do not fire again
        else:
            return False # no chance of multishot

    def calculate_round(self, library):
        # attacker fires and multishot is calculated on hit. If a firing
        #     ship hits a target it has multishot on then the firing
        #     ship has a (multishot - 1)/multishot chance of firing.
        #     Multishot will check again on each hit on a multishot target
        attacker_total_ships = self.ship_count(self.attacker_fleet)
        defender_total_ships = self.ship_count(self.defender_fleet)
        for ship_type in self.attacker_fleet:
            schema = library.get_ship_schemata(ship_type)
            for ship in self.attacker_fleet[ship_type]:
                while True:
                    if not fire_on(pick_random_ship(self.defender_fleet,
                                                    defender_total_ships),
                               schema.firepower, schema.multishot):
                            break
        # shield points are taken first (to zero, but not below)
        # armor points are taken second (to zero, but not below)
        # hull points are taken last

        # defender fires
        for ship_type in self.defender_fleet:
            schema = library.get_ship_schemata(ship_type)
            for ship in self.defender_fleet[ship_type]:
                while True:
                    if not fire_on(pick_random_ship(self.attacker_fleet,
                                                    attacker_total_ships),
                               schema.firepower, schema.multishot):
                            break
        # ships with 70% or less hull have a 1-hull/hull_initial chance
        #     to be reduced to zero hull
        # ships with zero hull are removed
        # all shield hitpoints are restored
        self.clean_dead_ships_restore_shields(self.attacker_fleet, library)
        self.clean_dead_ships_restore_shields(self.defender_fleet, library)

    def calculate_battle(self):
        # avoid using round as variable name as it's a predefined method
        # that might be useful when working with numbers.
        for r in xrange(self.rounds):
            self.calculate_round()

