from idleiss.universe import Universe
from idleiss.ship import ShipLibrary
from idleiss.battle import Battle
from idleiss.interpreter import Interpreter
import argparse
import os
import json
import random
#import networkx as nx
#import matplotlib.pyplot as plt
#import json

default_universe_config = 'config/Universe_Config.json'
default_ships_config = 'config/Ships_Config.json'
example_fleet_fight = 'config/Example_Fleet_Fight.json'

def run():
    parser = argparse.ArgumentParser(description='IdleISS: The Internet Spaceships IdleRPG')
    parser.add_argument('-u', '--universe', default=default_universe_config, dest='uniconfig', action='store', type=str,
        help='Set json universe settings file, if not provided the default {0} will be used'.format(default_universe_config))
    parser.add_argument('-s', '--ships', default=default_ships_config, dest='shipsconfig', action='store', type=str,
        help='Set json ships settings file, if not provided the default {0} will be used'.format(default_ships_config))
    parser.add_argument('--gen-maps', action='store_true', dest='genmaps',
        help='Generate the universe maps and put them in output/maps/ then exit')
    parser.add_argument('--simulate-battle', default=None, dest='simbattle',
        const=example_fleet_fight, nargs='?', action='store', type=str,
        help='Simulate a fleet fight between two fleets using a file and exit. Example file: {0}'.format(example_fleet_fight))
    parser.add_argument('-q', '--quick', action='store_true', dest='quickrun',
        help='Do not run the interpreter, only verify config files')

    one_shot_only = False

    args = parser.parse_args()
    if args.uniconfig != default_universe_config:
        print(f'Generating universe using alternate config: {args.uniconfig}')
    uni = Universe(args.uniconfig)
    print(uni.debug_output)
    print(f'Universe successfully loaded from {args.uniconfig}')
    if args.shipsconfig != default_ships_config:
        print(f'Loading starships using alternate config: {args.shipsconfig}')
    library = ShipLibrary(args.shipsconfig)
    print(f'Starships successfully loaded from {args.shipsconfig}: ')
    print(f'\tImported {len(library.ship_data)} ships')
    # map generation
    if args.genmaps:
        one_shot_only = True
        if not os.path.exists('output/maps'):
            os.makedirs('output/maps')
        print('\nGenerating region map and regional maps in /output/maps:')
        print('    generating {0} files:'.format(len(uni.regions)+1))
        region_graph = uni.generate_networkx(uni.regions)
        uni.save_graph(region_graph, 'output/maps/default_regions.png')
        print('=', end='', flush=True)
        for region in uni.regions:
            system_list = []
            for constellation in region.constellations:
                system_list.extend(constellation.systems)
            inter_region_graph = uni.generate_networkx(system_list)
            uni.save_graph(inter_region_graph, f'output/maps/default_region_{str(region.name)}.png')
            print('=', end='', flush=True)
        print('')
    # battle simulation
    if args.simbattle:
        one_shot_only = True
        #this must be a one_shot_due to random being reseeded
        random.seed()
        print(f'\nSimulating fleet fight using {args.simbattle}')
        raw_data = {}
        with open(args.simbattle) as fd:
            raw_data = json.load(fd)
        if type(raw_data) != dict:
            raise ValueError('--simulate-battle was not passed a json dictionary')
        battle_instance = Battle(raw_data['attacker'], raw_data['defender'],
                                 raw_data['rounds'], library)
        print(str(battle_instance.generate_summary_text()))
        print(f'\nBattle lasted {len(battle_instance.round_results)} rounds.')

    if not one_shot_only and not args.quickrun:
        # execute interpreter
        interp = Interpreter(args.uniconfig, args.shipsconfig)
        interp.run()

    # one_shot_only is True or interpreter has exited
    print('\nIdleISS exiting')
