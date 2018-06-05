from idleiss.universe import Universe
import argparse
import os
#import networkx as nx
#import matplotlib.pyplot as plt
#import json

def run():
    parser = argparse.ArgumentParser(description='IdleISS: The Internet Spaceships IdleRPG')
    parser.add_argument('-c', '--config', default='config/Universe_Config.json', dest='config', action='store', type=str,
        help='set config json universe settings file, if not provided the default config/Universe_Config.json will be used')
    parser.add_argument('--gen-maps', action='store_true', dest='genmaps',
        help='generate the universe maps and put them in /maps')

    args = parser.parse_args()
    if args.config != 'config/Universe_Config.json':
        print('Generating universe using '+args.config)
    uni = Universe(args.config)
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

    print('IdleISS exiting')
