from __future__ import division

import random
import math
from collections import namedtuple

from idleiss.ship import Ship
from idleiss.ship import ShipDebuffs
from idleiss.ship import ShipAttributes
from idleiss.ship import ShipLibrary

#SHIELD_BOUNCE_ZONE = 0.01  # max percentage damage to shield for bounce.
#HULL_DANGER_ZONE = 0.70  # percentage remaining.

AttackResult = namedtuple('AttackResult',
    ['attacker_fleet', 'damaged_fleet', 'hits_taken', 'damage_taken'])
Fleet = namedtuple('Fleet',
    ['ships', 'ship_count'])
RoundResult = namedtuple('RoundResult',
    ['ship_count', 'hits_taken', 'damage_taken'])


# def hull_breach(hull, max_hull, damage,
        # hull_danger_zone=HULL_DANGER_ZONE):
    # """
    # Hull has a chance of being breached if less than the dangerzone.
    # Chance of survival is determined by how much % hull remains.
    # Returns input hull amount if RNG thinks it should, otherwise 0.
    # """

    # damaged_hull = hull - damage
    # chance_of_survival = damaged_hull / max_hull
    # return not (chance_of_survival < hull_danger_zone and
        # chance_of_survival < random.random()) and damaged_hull or 0

# def shield_bounce(shield, max_shield, damage,
        # shield_bounce_zone=SHIELD_BOUNCE_ZONE):
    # """
    # Check whether the damage has enough power to damage the shield or
    # just harmlessly bounce off it, only if there is a shield available.
    # Shield will be returned if the above conditions are not met,
    # otherwise the current shield less damage taken will be returned.

    # Returns the new shield value.
    # """

    # # really, shield can't become negative unless some external factors
    # # hacked it into one.
    # return ((damage < shield * shield_bounce_zone) and shield > 0 and
        # shield or shield - damage)

def size_damage_factor(weapon_size, target_size):
    """
    Calculates damage factor on size.  If weapon size is greater than
    the target size, then only the area that falls within the target
    will the damage be applied.
    """

    if weapon_size <= target_size:
        return 1.0

    return (float(target_size) ** 2) / (float(weapon_size) ** 2)

def true_damage(damage, weapon_size, target_size, source_debuff, target_debuff):
    """
    Calculates true damage based on parameters.
    """

    # source_debuffs: tracking disruption
    tracking_disrupt = 1 + source_debuff.tracking_disruption

    # target_debuffs: target painter, web
    target_painter = 1 + target_debuff.target_painter
    web = max(1 - target_debuff.web, 0)

    # painters gives > 1 multiplier to the target_size against target
    # reason - painters expand the target to make it easier to hit.

    # webbers give < 1 multiplier to the weapon_size against target
    # reason - weapons can focus more damage on a webbed target

    if weapon_size * web * tracking_disrupt <=  \
            target_size * target_painter:
        return damage

    true_weapon_size = (weapon_size * web) * tracking_disrupt
    true_target_size = target_size * target_painter
    damage_factor = size_damage_factor(true_weapon_size, true_target_size)
    return int(math.ceil(damage_factor * damage))

def is_ship_alive(ship):
    """
    Simple check to see if ship is alive.
    """

    # If and when flag systems become advanced enough **FUN** things can
    # be applied to make this check more hilarious.
    return ship.attributes.hull > 0  # though it can't be < 0

def grab_debuffs(attacker_ship, victim_ship):
    """
    Debuff calculator.

    Returns a new ShipDebuffs tuple with the calculated values.
    """

    new_debuffs = attacker_ship.schema.debuffs
    current_debuffs = victim_ship.debuffs

    target_painter = max(
        new_debuffs.target_painter, current_debuffs.target_painter)

    tracking_disruption = max(
        new_debuffs.tracking_disruption, current_debuffs.tracking_disruption)

    # XXX break this out into its function as it's more complicated.
    ecm = 0
    if new_debuffs.ECM and not current_debuffs.ECM:
        if (victim_ship.schema.sensor_strength == 0 or
                random.random() < (float(
                    attacker_ship.schema.debuffs.ECM) / victim_ship.schema.sensor_strength)):
            ecm = new_debuffs.ECM

    web = max(new_debuffs.web, current_debuffs.web)

    return ShipDebuffs(target_painter, tracking_disruption, ecm, web)

def ship_attack(attacker_ship, victim_ship):
    """
    Do a ship attack.

    Apply the attacker's schema onto the victim_ship as an attack
    and return a new Ship object as the result.
    """

    if not is_ship_alive(victim_ship):
        # save us some time, it should be the same dead ship.
        return victim_ship

    if attacker_ship.debuffs.ECM:
        # attacker is jammed can't attack or apply debuffs
        return victim_ship

    debuffs = grab_debuffs(attacker_ship, victim_ship)

    if attacker_ship.schema.firepower <= 0:
    # damage doesn't need to be calculated, but debuffs do
        return Ship(
            victim_ship.schema,
            ShipAttributes(
                victim_ship.attributes.shield,
                victim_ship.attributes.armor,
                victim_ship.attributes.hull,
            ),
            debuffs,
        )

    damage = true_damage(attacker_ship.schema.firepower,
        attacker_ship.schema.weapon_size,
        victim_ship.schema.size,
        attacker_ship.debuffs,
        victim_ship.debuffs
    )
    if damage <= 0:
    #if damage modfiers change damage to 0 then victim takes no damage
        return Ship(
            victim_ship.schema,
            ShipAttributes(
                victim_ship.attributes.shield,
                victim_ship.attributes.armor,
                victim_ship.attributes.hull,
            ),
            debuffs,
        )

    shield = victim_ship.attributes.shield - damage
    armor = victim_ship.attributes.armor + min(shield, 0)
    hull = victim_ship.attributes.hull + min(armor, 0)
    return Ship(
        victim_ship.schema,
        ShipAttributes(max(0, shield), max(0, armor), max(0, hull)),
        debuffs,
    )

def expand_fleet(ship_count, library):
    # for the listing of numbers of ship we need to expand to each ship
    # having it's own value for shield, armor, and hull

    # TO DO: Make sure fleet when expanded is ordered by size
    #     From smallest to largest to make explode chance and
    #     shield bounce effects work out properly.

    ships = []
    for ship_type in ship_count:
        schema = library.get_ship_schemata(ship_type)
        ships.extend([Ship(
                schema,  # it's just a pointer...
                ShipAttributes(schema.shield, schema.armor, schema.hull),
            ) for i in range(ship_count[ship_type])])
    return Fleet(ships, ship_count)

def prune_fleet(attack_result):
    """
    Prune an AttackResult of dead ships and restore shields/armor.
    Returns the pruned fleet and a count of ships.
    """

    fleet = []
    count = {}
    damage_taken = 0

    for ship in attack_result.damaged_fleet:
        if not ship.attributes.hull > 0:
            continue

        fleet.append(Ship(
            ship.schema,
            ShipAttributes(
                min(ship.schema.shield,
                    (ship.attributes.shield + ship.schema.buffs.local_shield_repair)
                ),
                min(ship.schema.armor,
                    (ship.attributes.armor + ship.schema.buffs.local_armor_repair)
                ),
                ship.attributes.hull,
            ),
            ship.debuffs,
        ))
        count[ship.schema.name] = count.get(ship.schema.name, 0) + 1

    return Fleet(fleet, count)

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
        if ship.debuffs.ECM:
        # can't target to apply repairs
            continue
        if ship.schema.buffs.remote_shield_repair:
            logi_shield.append(ship)
        if ship.schema.buffs.remote_armor_repair:
            logi_armor.append(ship)
        else:
            continue
    return [logi_shield, logi_armor]

def priority_target_list(input_fleet, priority):
    """
    returns a list of numbers which correspond to the input_fleet positions
    which have the same hullclass as passed in parameter priority
    """
    subfleet = []
    for x in range(len(input_fleet)):
        if input_fleet[x].schema.hullclass in priority:
            subfleet.append(x)
        else:
            continue
    return subfleet

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
    for x in range(len(input_fleet)):
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
                            + ship.schema.buffs.remote_shield_repair)
                    ),
                    input_fleet[rep_target].attributes.armor,
                    input_fleet[rep_target].attributes.hull,
                ),
                input_fleet[rep_target].debuffs,
            )

    damaged_armor = []

    #armor second
    for x in range(len(input_fleet)):
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
                            + ship.schema.buffs.remote_armor_repair)
                    ),
                    input_fleet[rep_target].attributes.hull,
                ),
                input_fleet[rep_target].debuffs,
            )

    return input_fleet

def fleet_attack(fleet_a, fleet_b):
    """
    Do a round of fleet attack calculation.

    Send an attack from fleet_a to fleet_b.

    TODO?: Appends the hit_by attribute on the victim ship in fleet_b for
    each ship in fleet_a.
    """

    # if fleet b is empty
    if not fleet_b.ships:
        return AttackResult(fleet_a, fleet_b.ships, 0, 0)

    result = []
    result.extend(fleet_b.ships)
    shots = 0
    damage = 0

    for ship in fleet_a.ships:
        # Wanted to do apply an "attacked_by" attribute to
        # the target, but let's wait for that and just mutate this
        # into the new ship.  Something something hidden running
        # complexity when dealing with a list (it's an array).

        #TODO: implement priority targets
        #TODO: implement multiple weapons

        #TODO: FOR WEAPON IN WEAPONLIST:
        # some ships may not have damaging weapons, just debuffs. They don't increment "shots"
        if(ship.schema.firepower > 0):
            shots += 1

        # check if there are priority targets
        if ship.schema.priority_targets != []:
            target_found = False
            for possible_target in ship.schema.priority_targets:
                #for each priority level
                target_list = priority_target_list(result, possible_target)
                if target_list == []:
                    continue
                else: #target found
                    target_id = random.choice(target_list)
                    result[target_id] = ship_attack(ship, result[target_id])
                    target_found = True
                    break # only can shoot once per round per weapon
            if target_found == False: # no priority targets found shoot anything
                target_id = random.randrange(0, len(result))
                result[target_id] = ship_attack(ship, result[target_id])
        else: # if ship.priority_targets == {}
            target_id = random.randrange(0, len(result))
            result[target_id] = ship_attack(ship, result[target_id])



    # here all the ships have taken their shots and we sum for this round
    damage = sum((
            (fresh.attributes.shield - damaged.attributes.shield) +
            (fresh.attributes.armor - damaged.attributes.armor) +
            (fresh.attributes.hull - damaged.attributes.hull)
        for fresh, damaged in zip(fleet_b.ships, result)))

    return AttackResult(fleet_a.ships, result, shots, damage)


class Battle(object):
    """
    Battle between two fleets.

    To implement joint fleets, simply convert the attackers to a list of
    fleets, and create two lists and extend all member fleets into each
    one for the two respective sides.  Prune them separately for results.
    """

    def __init__(self, attacker, defender, max_rounds, *a, **kw):
        self.max_rounds = max_rounds
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

        defender_results = prune_fleet(defender_damaged)
        attacker_results = prune_fleet(attacker_damaged)

        # TODO figure out a better way to store round information that
        # can accommodate multiple fleets.

        self.round_results.append((
            RoundResult(attacker_results.ship_count,
                attacker_damaged.hits_taken, attacker_damaged.damage_taken),
            RoundResult(defender_results.ship_count,
                defender_damaged.hits_taken, defender_damaged.damage_taken),
        ))

        self.defender_fleet = defender_results
        self.attacker_fleet = attacker_results

    def calculate_battle(self):
        # avoid using round as variable name as it's a predefined method
        # that might be useful when working with numbers.
        for r in range(self.max_rounds):
            if not (self.defender_fleet.ships and self.attacker_fleet.ships):
                break
            self.calculate_round()

        # when/if we implement more than 1v1 then this will need to change
        self.attacker_result = self.round_results[-1][0].ship_count
        self.defender_result = self.round_results[-1][1].ship_count

    def generate_summary_data(self):
        """
        TODO: Generate all the data (see test)
        """
        pass

    def generate_summary_text(self):
        """
        TODO: Generate ASCII style text output
        """
        pass
