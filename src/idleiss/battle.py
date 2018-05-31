from __future__ import division

import random
import math
from collections import namedtuple

from idleiss.ship import Ship
from idleiss.ship import ShipDebuffs
from idleiss.ship import ShipAttributes
from idleiss.ship import ShipLibrary

AttackResult = namedtuple('AttackResult',
    ['attacker_fleet', 'damaged_fleet', 'hits_taken', 'damage_taken'])
Fleet = namedtuple('Fleet',
    ['ships', 'ship_count'])
RoundResult = namedtuple('RoundResult',
    ['ship_count', 'hits_taken', 'damage_taken'])

def size_damage_factor(weapon_size, target_size):
    """
    Calculates damage factor on size.  If weapon size is greater than
    the target size, then only the area that falls within the target
    will the damage be applied.
    """

    if weapon_size <= target_size:
        return 1.0

    return (float(target_size) ** 2) / (float(weapon_size) ** 2)

def true_damage(damage, weapon_size, target_size, attacker_debuffs, target_debuff):
    """
    Calculates true damage based on parameters.
    """

    # source_debuffs: tracking disruption
    tracking_disrupt = 1 + attacker_debuffs.tracking_disruption

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
    if damage_factor * damage < 0:
        return 0
    return int(math.ceil(damage_factor * damage))

def is_ship_alive(ship):
    """
    Simple check to see if ship is alive.
    """

    # If and when flag systems become advanced enough **FUN** things can
    # be applied to make this check more hilarious.
    return ship.attributes.hull > 0  # though it can't be < 0

def grab_debuffs(attacker_weapon, victim_ship):
    """
    Debuff calculator.

    Returns a new ShipDebuffs tuple with the calculated values.
    """

    if victim_ship.schema.ecm_immune:
        return ShipDebuffs(0, 0, 0, 0)

    new_debuffs = attacker_weapon.get('debuffs',{})
    current_debuffs = victim_ship.debuffs

    target_painter = max(
        new_debuffs.get('target_painter',0), current_debuffs.target_painter)

    tracking_disruption = max(
        new_debuffs.get('tracking_disruption',0), current_debuffs.tracking_disruption)

    # XXX break this out into its function as it's more complicated.
    ecm = 0
    if new_debuffs.get('ECM',0) != 0 and not current_debuffs.ECM:
        if (victim_ship.schema.sensor_strength == 0 or
                random.random() < (float(
                    new_debuffs['ECM']) / victim_ship.schema.sensor_strength)):
            ecm = new_debuffs['ECM']

    web = max(new_debuffs.get('web',0), current_debuffs.web)

    return ShipDebuffs(target_painter, tracking_disruption, ecm, web)

def ship_attack(attacker_weapon, attacker_debuffs, victim_ship):
    """
    Do a ship attack.

    Apply the attacker's schema onto the victim_ship as an attack
    and return a new Ship object as the result.
    """

    if not is_ship_alive(victim_ship):
        # save us some time, it could be the same dead ship.
        return victim_ship

    if victim_ship.schema.is_structure:
        # strucutres should not be attacked during fleet fights
        # structure damage and destruction is another mechanic outside of fleet engagements
        raise ValueError("Battle.ship_attack() encountered a structure as a victim_ship")

    debuffs = grab_debuffs(attacker_weapon, victim_ship)

    if attacker_weapon['firepower'] <= 0:
    # no weapons: damage doesn't need to be calculated, but debuffs do
        return Ship(
            victim_ship.schema,
            ShipAttributes(
                victim_ship.attributes.shield,
                victim_ship.attributes.armor,
                victim_ship.attributes.hull,
            ),
            debuffs,
        )

    damage = true_damage(attacker_weapon['firepower'],
        attacker_weapon['weapon_size'],
        victim_ship.schema.size,
        attacker_debuffs,
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

def strucutre_list(input_fleet):
    """
    returns a list of ships where ship.schema.is_structure is True
    """
    subfleet = []
    for x in range(len(input_fleet)):
        if input_fleet[x].schema.is_structure == True:
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

    # this has a slight bug that ships can rep themselves
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

def fleet_attack(fleet_a, fleet_b, current_round_number):
    """
    Do a round of fleet attack calculation.

    Send an attack from fleet_a to fleet_b on round current_round_number.

    current_round_number determines which weapons are fired (on 0 all are fired)

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

        if ship.debuffs.ECM:
            # attacker is jammed can't attack or apply debuffs
            continue

        for weapon in ship.schema.weapons:
            #if it isn't time for the weapon to cycle then do not do anything for this weapon
            if current_round_number % weapon['cycle_time'] != 0:
                continue

            # weapons increment shots by 1 if the weapon firepower is > 0
            if weapon['firepower'] > 0:
                shots += 1

            aoe_hit_list = []
            structures = strucutre_list(result)
            #repeat for each "area_of_effect" count
            for area_of_effect in range(weapon['area_of_effect']):
                # check if there are priority targets
                if weapon['priority_targets'] != []:
                    target_found = False
                    for possible_target in weapon['priority_targets']:
                        # for each priority level
                        target_list = priority_target_list(result, possible_target)
                        # aoe weapons cannot hit the same target twice
                        target_list = list(set(target_list) - set(aoe_hit_list) - set(structures))
                        if target_list == []: # no target
                            continue # try next priority level

                        # target found
                        target_id = random.choice(target_list)
                        result[target_id] = ship_attack(weapon, ship.debuffs, result[target_id])
                        aoe_hit_list.append(target_id)
                        target_found = True
                        break # only can hit once per loop
                    #end of priority_targets for loop

                    if target_found == False: # no priority targets found shoot anything
                        #aoe weapons cannot hit the same target twice
                        target_list = list(set(range(len(result))) - set(aoe_hit_list) - set(structures))
                        if target_list == []:
                            continue # no remaining targets for AOE

                        target_id = random.choice(target_list)
                        result[target_id] = ship_attack(weapon, ship.debuffs, result[target_id])
                        aoe_hit_list.append(target_id)
                else: # this means: weapon['priority_targets'] is [] (empty)
                    target_list = list(set(range(len(result))) - set(aoe_hit_list) - set(structures))
                    if target_list == []:
                        continue # no remaining targets for AOE

                    target_id = random.choice(target_list)
                    result[target_id] = ship_attack(weapon, ship.debuffs, result[target_id])
                    aoe_hit_list.append(target_id)
            #end of area_of_effect for loop

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

    def __init__(self, attacker, defender, max_rounds, library,  *a, **kw):
        """
            attacker: dictionary with "ship_type": number
            defender: dictionary with "ship_type": number
            max_rounds: number of rounds battle will calulate
            library: ship library to use

            __init__ will automatically generate results once called
        """
        # kwargs:
        #     calculate: DEBUG/TEST kwarg to stop automatic battle calculation if False

        self.max_rounds = max_rounds
        # attacker and defender are dictionaries with "ship_type": number
        self.attacker_count = attacker
        self.defender_count = defender

        self.attacker_fleet = self.defender_fleet = None

        self.round_results = []
        self.prepare(library)
        if(kw.get('calculate', True) != False):
            self.calculate_battle()

    def prepare(self, library):
        # do all the fleet preparation pre-battle using this game
        # library.  Could be called initialize.
        self.stored_library = library
        self.attacker_fleet = expand_fleet(self.attacker_count, library)
        self.defender_fleet = expand_fleet(self.defender_count, library)

    def calculate_round(self, current_round_number):
        defender_damaged = fleet_attack(
            self.attacker_fleet, self.defender_fleet, current_round_number)
        attacker_damaged = fleet_attack(
            self.defender_fleet, self.attacker_fleet, current_round_number)

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
            self.calculate_round(r)

        # when/if we implement more than 1v1 then this will need to change
        self.attacker_result = self.round_results[-1][0].ship_count
        self.defender_result = self.round_results[-1][1].ship_count

    def generate_summary_data(self):
        attacker_shots = 0
        defender_shots = 0
        attacker_damage_dealt = 0
        defender_damage_dealt = 0
        for round_result in self.round_results:
            attacker_shots += round_result[1].hits_taken
            defender_shots += round_result[0].hits_taken
            attacker_damage_dealt += round_result[1].damage_taken
            defender_damage_dealt += round_result[0].damage_taken
        attacker_losses = {key: self.attacker_count[key] - self.attacker_result.get(key, 0) for key in self.attacker_count.keys()}
        defender_losses = {key: self.defender_count[key] - self.defender_result.get(key, 0) for key in self.defender_count.keys()}
        return {
            "attacker_fleet": self.attacker_count,
            "defender_fleet": self.defender_count,
            "attacker_result": self.attacker_result,
            "attacker_losses": attacker_losses,
            "attacker_shots_fired": attacker_shots,
            "attacker_damage_dealt": attacker_damage_dealt,
            "defender_result": self.defender_result,
            "defender_losses": defender_losses,
            "defender_shots_fired": defender_shots,
            "defender_damage_dealt": defender_damage_dealt
        }

    def generate_summary_text(self):
        summary = self.generate_summary_data()
        outstr = "Attacker:\n"
        attacker_fleet = summary['attacker_fleet']
        attacker_ships = []
        for key in attacker_fleet:
            attacker_ships.append(key)
        attacker_ships.sort()
        attacker_ships.sort(key=lambda s: self.stored_library.get_ship_schemata(s).sortclass)
        for attacking_ship in attacker_ships:
            outstr += "    %s: %i\n" % (attacking_ship, summary['attacker_fleet'][attacking_ship])
        outstr += "Defender:\n"
        defender_fleet = summary['defender_fleet']
        if len(defender_fleet) == 0:
            outstr += "    NO DEFENDING SHIPS\n"
        else:
            defender_ships = []
            for key in defender_fleet:
                defender_ships.append(key)
            defender_ships.sort()
            defender_ships.sort(key=lambda s: self.stored_library.get_ship_schemata(s).sortclass)
            for defending_ship in defender_ships:
                outstr += "    %s: %i\n" % (defending_ship, summary['defender_fleet'][defending_ship])
        outstr += "\nResult:\nAttacker:\n"
        attacker_fleet_result = summary['attacker_result']
        if len(attacker_fleet_result) == 0:
            outstr += "    ALL ATTACKING SHIPS DESTROYED\n"
        else:
            attacker_result = []
            for key in attacker_fleet_result:
                attacker_result.append(key)
            attacker_result.sort()
            attacker_result.sort(key=lambda s: self.stored_library.get_ship_schemata(s).sortclass)
            for attacking_ship in attacker_result:
                outstr += "    %s: %i (Lost: %i)\n" % (attacking_ship, attacker_fleet_result[attacking_ship], summary['attacker_losses'][attacking_ship])
        outstr += "Defender:\n"
        defender_fleet_result = summary['defender_result']
        if len(defender_fleet_result) == 0:
            outstr += "    ALL DEFENDING SHIPS DESTROYED"
        else:
            defender_result = []
            for key in defender_fleet_result:
                defender_result.append(key)
            defender_result.sort()
            defender_result.sort(key=lambda s: self.stored_library.get_ship_schemata(s).sortclass)
            for defending_ship in defender_result:
                outstr += "    %s: %i (Lost: %i)\n" % (defending_ship, defender_fleet_result[defending_ship], summary['defender_losses'][defending_ship])
        return outstr.rstrip()
