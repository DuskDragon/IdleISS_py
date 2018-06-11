from idleiss.universe import Universe
from idleiss.ship import ShipLibrary
import argparse
import os
#import networkx as nx
#import matplotlib.pyplot as plt
#import json

default_universe_config = 'config/Universe_Config.json'
default_ships_config = 'config/Ships_Config.json'

def run():
    parser = argparse.ArgumentParser(description='IdleISS: The Internet Spaceships IdleRPG')
    parser.add_argument('-u', '--universe', default=default_universe_config, dest='uniconfig', action='store', type=str,
        help='set json universe settings file, if not provided the default {0} will be used'.format(default_universe_config))
    parser.add_argument('-s', '--ships', default=default_ships_config, dest='shipsconfig', action='store', type=str,
        help='set json ships settings file, if not provided the default {0} will be used'.format(default_ships_config))
    parser.add_argument('--gen-maps', action='store_true', dest='genmaps',
        help='generate the universe maps and put them in output/maps/')

    args = parser.parse_args()
    if args.uniconfig != default_universe_config:
        print(f'Generating universe using alternate config: {args.uniconfig}')
    uni = Universe(args.uniconfig)
    print(f'\nUniverse successfully loaded from {args.uniconfig}')
    if args.shipsconfig != default_ships_config:
        print(f'Loading starships using alternate config: {args.shipsconfig}')
    library = ShipLibrary(args.shipsconfig)
    print(f'Starships successfully loaded from {args.shipsconfig}: ')
    print(f'\tImported {len(library.ship_data)} ships')
    if args.genmaps:
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
            uni.save_graph(inter_region_graph, 'output/maps/default_region_'+str(region.name)+'.png')
            print('=', end='', flush=True)
        print('')

    print('\nIdleISS exiting')
