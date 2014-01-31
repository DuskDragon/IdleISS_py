import random
from collections import namedtuple

from idleiss.ship import Ship
from idleiss.ship import ShipAttributes
from idleiss.ship import ShipLibrary

SHIELD_BOUNCE_ZONE = 0.01  # max percentage damage to shield for bounce.
HULL_DANGER_ZONE = 0.70  # percentage remaining.

PrunedFleet = namedtuple('PrunedFleet', ['fleet', 'count', 'damage_taken'])


def hull_breach(hull, max_hull,
        hull_danger_zone=HULL_DANGER_ZONE):
    """
    Hull has a chance of being breached if less than the dangerzone.
    Chance of survival is determined by how much % hull remains.
    Returns input hull amount if RNG thinks it should, otherwise 0.
    """
    chance_of_survival = (float(hull) / float(max_hull))
    return not (chance_of_survival < hull_danger_zone and
        chance_of_survival < random.random()) and hull or 0

def shield_bounce(shield, max_shield, firepower,
        shield_bounce_zone=SHIELD_BOUNCE_ZONE):
    """
    Check whether the firepower has enough power to damage the shield or
    just harmlessly bounce off it, only if there is a shield available.
    Shield will be returned if the above conditions are not met,
    otherwise the shield less firepower or negative firepower will be
    returned.

    Returns the new shield value.
    """

    # really, shield can't become negative unless some external factors
    # hacked it into one.
    return ((firepower < max_shield * shield_bounce_zone) and shield > 0 and
        shield or shield - firepower)

def is_ship_alive(ship):
    """
    Simple check to see if ship is alive.
    """

    # If and when flag systems become advanced enough **FUN** things can
    # be applied to make this check more hilarious.
    return ship.attributes.hull > 0  # though it can't be < 0

def ship_attack(attacker_schema, victim_ship):
    """
    Do a ship attack.

    Apply the attacker's schema onto the victim_ship as an attack
    and return a new Ship object as the result.
    """

    if not is_ship_alive(victim_ship):
        # save us some time, it should be the same dead ship.
        return victim_ship

    shield = shield_bounce(victim_ship.attributes.shield,
        victim_ship.schema.shield, attacker_schema.firepower)
    armor = victim_ship.attributes.armor + min(shield, 0)
    hull = hull_breach(victim_ship.attributes.hull + min(armor, 0),
        victim_ship.schema.hull)
    return Ship(victim_ship.schema,
        ShipAttributes(max(0, shield), max(0, armor), max(0, hull)))

def multishot(attacker_schema, victim_schema):
    """
    Calculate multishot result based on the schemas.
    """

    multishot = attacker_schema.multishot.get(victim_schema.name, 0)
    return multishot > 0 and (multishot - 1.0) / multishot > random.random()

def prune_fleet(damaged_fleet):
    """
    Prune a damaged fleet of dead ships and restore the shields.
    Returns the pruned fleet and a count of ships.
    """

    fleet = []
    count = {}
    damage_taken = 0

    for ship in damaged_fleet:
        if not ship.attributes.hull > 0:
            continue

        # damage_taken can't be calculated now as armor might not have
        # been damaged this round.  Need actual damage information.

        # I considered doing another attribute to ship for temporary
        # afflictions, such as damage/ecm and the like will be tagged
        # onto that dict, but for now we leave that out.

        fleet.append(Ship(
            ship.schema,
            ShipAttributes(
                ship.schema.shield,
                ship.attributes.armor,
                ship.attributes.hull,
            ),
        ))
        count[ship.schema.name] = count.get(ship.schema.name, 0) + 1

    return PrunedFleet(fleet, count, damage_taken)

def fleet_attack(fleet_a, fleet_b):
    """
    Do a round of fleet attack calculation.

    Send an attack from fleet_a to fleet_b.

    Appends the hit_by attribute on the victim ship in fleet_b for
    each ship in fleet_a.
    """

    # if fleet b is empty
    if not fleet_b:
        # nothing for fleet_a to attack, and we are going to get back the
        # same dumb fleet.
        return fleet_b

    result = []
    result.extend(fleet_b)

    for ship in fleet_a:
        firing = True
        # I kind of wanted to do apply an "attacked_by" attribute to
        # the target, but let's wait for that and just mutate this
        # into the new ship.  Something something hidden running
        # complexity when dealing with a list (it's an array).
        while firing:
            target_id = random.randrange(0, len(result))
            result[target_id] = ship_attack(ship.schema, result[target_id])
            firing = multishot(ship.schema, result[target_id].schema)

    return result


class Battle(object):
    """
    Battle between two fleets.

    To implement joint fleets, simply convert the attackers to a list of
    fleets, and create two lists and extend all member fleets into each
    one for the two respective sides.  Prune them separately for results.
    """

    def __init__(self, attacker, defender, rounds, *a, **kw):
        self.rounds = rounds
        # attacker and defender are dictionaries with "ship_type": number
        self.attacker_count = attacker
        self.defender_count = defender

        self.attacker_fleet = self.defender_fleet = None

        self.round_results = []

    def expand(self, fleet, library):
        # for the listing of numbers of ship we need to expand to each ship
        # having it's own value for shield, armor, and hull

        # TO DO: Make sure fleet when expanded is ordered by size
        #     From smallest to largest to make explode chance and
        #     shield bounce effects work out properly.

        ships = []
        for ship_type in fleet:
            schema = library.get_ship_schemata(ship_type)
            ships.extend([Ship(
                    schema,  # it's just a pointer...
                    ShipAttributes(schema.shield, schema.armor, schema.hull),
                ) for i in range(fleet[ship_type])])
        return ships

    def prepare(self, library):
        # do all the fleet preparation pre-battle using this game
        # library.  Could be called initialize.
        self.attacker_fleet = self.expand(self.attacker_count, library)
        self.defender_fleet = self.expand(self.defender_count, library)

    def calculate_round(self):
        # really could return a result, but :effort:
        self.defender_fleet = fleet_attack(
            self.attacker_fleet, self.defender_fleet)
        self.attacker_fleet = fleet_attack(
            self.defender_fleet, self.attacker_fleet)

        defender_results = prune_fleet(self.defender_fleet)
        attacker_results = prune_fleet(self.attacker_fleet)

        # TODO figure out a better way to store round information that
        # can accommodate multiple fleets.

        self.round_results.append((attacker_results, defender_results))

        self.defender_fleet = defender_results.fleet
        self.attacker_fleet = attacker_results.fleet

    def calculate_battle(self):
        # avoid using round as variable name as it's a predefined method
        # that might be useful when working with numbers.
        for r in xrange(self.rounds):
            if not (self.defender_fleet and self.attacker_fleet):
                break
            self.calculate_round()

