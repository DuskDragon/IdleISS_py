from __future__ import division

import random
import math
from collections import namedtuple

from idleiss.ship import Ship
from idleiss.ship import ShipAttributes
from idleiss.ship import ShipLibrary

SHIELD_BOUNCE_ZONE = 0.01  # max percentage damage to shield for bounce.
HULL_DANGER_ZONE = 0.70  # percentage remaining.

AttackResult = namedtuple('AttackResult',
    ['attacker_fleet', 'damaged_fleet', 'shots_taken', 'damage_taken'])
PrunedFleet = namedtuple('PrunedFleet',
    ['fleet', 'ship_count'])
RoundResult = namedtuple('RoundResult',
    ['ship_count', 'shots_taken', 'damage_taken'])


def hull_breach(hull, max_hull, damage,
        hull_danger_zone=HULL_DANGER_ZONE):
    """
    Hull has a chance of being breached if less than the dangerzone.
    Chance of survival is determined by how much % hull remains.
    Returns input hull amount if RNG thinks it should, otherwise 0.
    """

    damaged_hull = hull - damage
    chance_of_survival = damaged_hull / max_hull
    return not (chance_of_survival < hull_danger_zone and
        chance_of_survival < random.random()) and damaged_hull or 0

def shield_bounce(shield, max_shield, damage,
        shield_bounce_zone=SHIELD_BOUNCE_ZONE):
    """
    Check whether the damage has enough power to damage the shield or
    just harmlessly bounce off it, only if there is a shield available.
    Shield will be returned if the above conditions are not met,
    otherwise the current shield less damage taken will be returned.

    Returns the new shield value.
    """

    # really, shield can't become negative unless some external factors
    # hacked it into one.
    return ((damage < shield * shield_bounce_zone) and shield > 0 and
        shield or shield - damage)

def true_damage(damage, weapon_size, target_size, source_debuff, target_debuff):
    """
    Calculates true damage.  If weapon size is greater than the target
    size, then only the area that falls within the target will the
    damage be applied.  Round up to the nearest integer.
    """

    # source_debuffs: tracking disruption
    tracking_disrupt = 1 + source_debuff.get('active', {}).get(
        'tracking_disruption', 0)
    # target_debuffs: target painter, web
    target_painter = 1 + target_debuff.get('active', {}).get(
        'target_painter', 0)
    web = 1 - target_debuff.get('active', {}).get(
        'web', 0)

    # painters gives > 1 multiplier to the target_size against target
    # reason - painters expand the target to make it easier to hit.

    # webbers give < 1 multiplier to the weapon_size against target
    # reason - weapons can focus more damage on a webbed target

    if web == 0 or weapon_size / web * tracking_disrupt <=  \
        target_size * target_painter:
        return damage

    return int(math.ceil((((target_size * target_painter) ** 2) /
        (((weapon_size / web) * tracking_disrupt) ** 2)) *
        damage))

def is_ship_alive(ship):
    """
    Simple check to see if ship is alive.
    """

    # If and when flag systems become advanced enough **FUN** things can
    # be applied to make this check more hilarious.
    return ship.attributes.hull > 0  # though it can't be < 0

def grab_debuffs(source, target_in):
    """
    Retuns a dict of applied debufs calculated from ship schema
    as well as ship attributes.
    Source is ShipSchema
    target_in is a Ship
    These debuffs are 'inactive' so they are for next turn
    """
    result = {}
    sensor_str = target_in.schema.sensor_strength
    target = target_in.attributes
    # I'm sure there's a list comprehension thing that could be used
    # to clean this up but I have no idea what
    if source.target_painter:
        if target.debuffs.get('inactive', {}).get('target_painter', 0) < \
            source.target_painter:
                result['target_painter'] = source.target_painter
    if source.tracking_disruption:
        if target.debuffs.get('inactive', {}).get('tracking_disruption', 0) < \
            source.tracking_disruption:
                result['tracking_disruption'] = source.tracking_disruption
    if source.ECM:
        if not target.debuffs.get('inactive', {}).get('ECM', 0):
            if sensor_str == 0 or \
                random.random() < (float(source.ECM) / sensor_str):
                    result['ECM'] = source.ECM
    if source.web:
        if target.debuffs.get('inactive', {}).get('web', 0) < source.web:
                result['web'] = source.web
    return { 'inactive': result, 'active': target.debuffs.get('active', {}) }

def ship_attack(attacker_schema, victim_ship, attacker_debuffs):
    """
    Do a ship attack.

    Apply the attacker's schema onto the victim_ship as an attack
    and return a new Ship object as the result.
    """

    if not is_ship_alive(victim_ship):
        # save us some time, it should be the same dead ship.
        return victim_ship

    if attacker_debuffs.get('active', {}).get('ECM', 0) != 0:
        # attacker is jammed can't attack or apply debuffs
        return victim_ship

    debuffs = grab_debuffs(attacker_schema, victim_ship)

    if attacker_schema.firepower <= 0:
    # damage doesn't need to be calculated, but debuffs do
        return Ship(victim_ship.schema,
            ShipAttributes(victim_ship.attributes.shield,
                           victim_ship.attributes.armor,
                           victim_ship.attributes.hull, debuffs))

    damage = true_damage(attacker_schema.firepower,
        attacker_schema.weapon_size,
        victim_ship.schema.size,
        attacker_debuffs,
        victim_ship.attributes.debuffs
    )

    shield = shield_bounce(victim_ship.attributes.shield,
        victim_ship.schema.shield, damage)
    if shield == victim_ship.attributes.shield:
        # it glanced off, don't need to worry about hull breaches when
        # the weapon didn't even hit
        return Ship(victim_ship.schema,
        ShipAttributes(victim_ship.attributes.shield,
                       victim_ship.attributes.armor,
                       victim_ship.attributes.hull, debuffs))

    armor = victim_ship.attributes.armor + min(shield, 0)
    hull = hull_breach(victim_ship.attributes.hull,
        victim_ship.schema.hull, - min(armor, 0))
    return Ship(victim_ship.schema,
        ShipAttributes(max(0, shield), max(0, armor), max(0, hull), debuffs))

def multishot(attacker_schema, victim_schema):
    """
    Calculate multishot result based on the schemas.
    """

    multishot = attacker_schema.multishot.get(victim_schema.hullclass, 0)
    return multishot > 0 and (multishot - 1.0) / multishot > random.random()

def expand_fleet(fleet, library):
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
                ShipAttributes(schema.shield, schema.armor, schema.hull, {}),
            ) for i in range(fleet[ship_type])])
    return ships

def prune_fleet(damaged_fleet):
    """
    Prune a damaged fleet of dead ships and restore shields/armor.
    Returns the pruned fleet and a count of ships.
    """

    fleet = []
    count = {}
    damage_taken = 0

    for ship in damaged_fleet:
        if not ship.attributes.hull > 0:
            continue

        updated_debuffs = {}
        updated_debuffs['active'] = ship.attributes.debuffs.get('inactive', {})
        # switch the inactive debuffs to active and drop current active ones

        fleet.append(Ship(
            ship.schema,
            ShipAttributes(
                min(ship.schema.shield,
                    (ship.attributes.shield + ship.schema.shield_recharge)
                ),
                min(ship.schema.armor,
                    (ship.attributes.armor + ship.schema.armor_local_repair)
                ),
                ship.attributes.hull,
                updated_debuffs,
            ),
        ))
        count[ship.schema.name] = count.get(ship.schema.name, 0) + 1

    return PrunedFleet(fleet, count)

def logi_subfleet(input_fleet):
    """
    returns two sub_fleets of logi ships that can rep
    [0]: shield
    [1]: armor
    ships which are jammed this turn are not entered into the list
    """
    logi_shield = []
    logi_armor = []
    for ship in input_fleet:
        if ship.attributes.debuffs.get('active', {}).get('ECM', 0) != 0:
        # can't target to apply repairs
            continue
        if ship.schema.remote_shield:
            logi_shield.append(ship)
        if ship.schema.remote_armor:
            logi_armor.append(ship)
        else:
            continue
    return [logi_shield, logi_armor]

def repair_fleet(input_fleet):
    """
    Have logistics ships do their job and repair other ships in the fleet
    """
    logistics = logi_subfleet(input_fleet)
    logi_shield = logistics[0]
    logi_armor = logistics[1]
    if (logi_shield == []) and (logi_armor == []):
        return input_fleet

    damaged_shield = []

    # I have a bad feeling that this function won't last longer
    # than a single commit :ohdear:
    # also this has a slight bug that ships can rep themselves
    # and a ship might get over repped, but that's actually intended

    # shield first
    for x in xrange(len(input_fleet)):
        if input_fleet[x].attributes.shield != input_fleet[x].schema.shield:
            damaged_shield.append(x)

    if damaged_shield != []:
        for ship in logi_shield:
            rep_target = random.choice(damaged_shield)
            input_fleet[rep_target] = Ship(
                input_fleet[rep_target].schema,
                ShipAttributes(
                    min(input_fleet[rep_target].schema.shield,
                        (input_fleet[rep_target].attributes.shield
                            + ship.schema.remote_shield)
                    ),
                    input_fleet[rep_target].attributes.armor,
                    input_fleet[rep_target].attributes.hull,
                    input_fleet[rep_target].attributes.debuffs,
                ),
            )

    damaged_armor = []

    #armor second
    for x in xrange(len(input_fleet)):
        if input_fleet[x].attributes.armor != input_fleet[x].schema.armor:
            damaged_armor.append(int(x))

    if damaged_armor != []:
        for ship in logi_armor:
            rep_target = random.choice(damaged_armor)
            input_fleet[rep_target] = Ship(
                input_fleet[rep_target].schema,
                ShipAttributes(
                    input_fleet[rep_target].attributes.shield,
                    min(input_fleet[rep_target].schema.armor,
                        (input_fleet[rep_target].attributes.armor
                            + ship.schema.remote_armor)
                    ),
                    input_fleet[rep_target].attributes.hull,
                    input_fleet[rep_target].attributes.debuffs,
                ),
            )

    return input_fleet

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
    shots = 0
    damage = 0

    for ship in fleet_a:
        firing = True
        # I kind of wanted to do apply an "attacked_by" attribute to
        # the target, but let's wait for that and just mutate this
        # into the new ship.  Something something hidden running
        # complexity when dealing with a list (it's an array).
        while firing:
            target_id = random.randrange(0, len(result))
            result[target_id] = ship_attack(ship.schema, result[target_id],
                ship.attributes.debuffs)
            firing = multishot(ship.schema, result[target_id].schema)
            shots += 1

    damage = sum((
            (fresh.attributes.shield - damaged.attributes.shield) +
            (fresh.attributes.armor - damaged.attributes.armor) +
            (fresh.attributes.hull - damaged.attributes.hull)
        for fresh, damaged in zip(fleet_b, result)))

    return AttackResult(fleet_a, result, shots, damage)


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

    def prepare(self, library):
        # do all the fleet preparation pre-battle using this game
        # library.  Could be called initialize.
        self.attacker_fleet = expand_fleet(self.attacker_count, library)
        self.defender_fleet = expand_fleet(self.defender_count, library)

    def calculate_round(self):
        defender_damaged = fleet_attack(
            self.attacker_fleet, self.defender_fleet)
        attacker_damaged = fleet_attack(
            self.defender_fleet, self.attacker_fleet)

        attacker_repaired = repair_fleet(attacker_damaged.damaged_fleet)
        defender_repaired = repair_fleet(defender_damaged.damaged_fleet)

        defender_results = prune_fleet(defender_repaired)
        attacker_results = prune_fleet(attacker_repaired)

        # TODO figure out a better way to store round information that
        # can accommodate multiple fleets.

        self.round_results.append((
            RoundResult(attacker_results.ship_count,
                attacker_damaged.shots_taken, attacker_damaged.damage_taken),
            RoundResult(defender_results.ship_count,
                defender_damaged.shots_taken, defender_damaged.damage_taken),
        ))

        self.defender_fleet = defender_results.fleet
        self.attacker_fleet = attacker_results.fleet

    def calculate_battle(self):
        # avoid using round as variable name as it's a predefined method
        # that might be useful when working with numbers.
        for r in xrange(self.rounds):
            if not (self.defender_fleet and self.attacker_fleet):
                break
            self.calculate_round()

        # when/if we implement more than 1v1 then this will need to change
        self.attacker_result = self.round_results[-1][0].ship_count
        self.defender_result = self.round_results[-1][1].ship_count
