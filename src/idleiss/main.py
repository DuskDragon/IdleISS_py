from idleiss.universe import Universe
from idleiss.ship import ShipLibrary
from idleiss.battle import Battle
from idleiss.interpreter import Interpreter
import argparse
import os
import json
import random


default_universe_config = "config/Universe_Config.json"
default_ships_config = "config/Ships_Config.json"
example_fleet_fight = "config/Example_Fleet_Fight.json"

def run():
    parser = argparse.ArgumentParser(description="IdleISS: The Internet Spaceships IdleRPG")
    parser.add_argument("-u", "--universe", default=default_universe_config, dest="uniconfig", action="store", type=str,
        help=f"Set json universe settings file, if not provided the default {default_universe_config} will be used")
    parser.add_argument("-s", "--ships", default=default_ships_config, dest="shipsconfig", action="store", type=str,
        help=f"Set json ships settings file, if not provided the default {default_ships_config} will be used")
    parser.add_argument("--gen-maps", action="store_true", dest="genmaps",
        help="Generate the universe maps and put them in output/maps/ then exit")
    parser.add_argument("--simulate-battle", default=None, dest="simbattle",
        const=example_fleet_fight, nargs="?", action="store", type=str,
        help=f"Simulate a fleet fight between two fleets using a file and exit. Example file: {example_fleet_fight}")
    parser.add_argument("-q", "--quick", action="store_true", dest="quickrun",
        help="Do not run the interpreter, only verify config files")
    parser.add_argument("--preload", dest="interpreter_preload", action="store", type=str,
        help="if the interpreter is executed then this file will be used as the initial commands before control is "
             "given to the user")
    parser.add_argument("--log-interpreter", action="store_true", dest="interpreter_log_enable",
        help="Enable interpreter logs for future playback. Logs are stored in interpreter_log.txt")

    one_shot_only = False

    args = parser.parse_args()
    if args.uniconfig != default_universe_config:
        print(f"Generating universe using alternate config: {args.uniconfig}")
    uni = Universe(args.uniconfig)
    print(''.join(uni.debug_output))
    print(f"Universe successfully loaded from {args.uniconfig}")
    if args.shipsconfig != default_ships_config:
        print(f"Loading starships using alternate config: {args.shipsconfig}")
    library = ShipLibrary(args.shipsconfig)
    print(f"Starships successfully loaded from {args.shipsconfig}: ")
    print(f"\tImported {len(library.ship_data)} ships")
    # map generation
    if args.genmaps:
        one_shot_only = True
        if not os.path.exists("output/maps"):
            os.makedirs("output/maps")
        print("\nGenerating region map and regional maps in /output/maps:")
        print(f"    generating {len(uni.regions)+1} files:")
        region_graph = uni.generate_networkx(uni.regions)
        uni.save_graph(region_graph, "output/maps/default_regions.png")
        print("=", end="", flush=True)
        for region in uni.regions:
            system_list = []
            for constellation in region.constellations:
                system_list.extend(constellation.systems)
            inter_region_graph = uni.generate_networkx(system_list)
            uni.save_graph(inter_region_graph, f"output/maps/default_region_{str(region.name)}.png")
            print("=", end="", flush=True)
        print("")
    # battle simulation
    if args.simbattle:
        one_shot_only = True
        # this must be a one_shot_due to random being reseeded
        random.seed()
        print(f"\nSimulating fleet fight using {args.simbattle}")
        raw_data = {}
        with open(args.simbattle) as fd:
            raw_data = json.load(fd)
        if type(raw_data) != dict:
            raise ValueError("--simulate-battle was not passed a json dictionary")
        battle_instance = Battle(raw_data["attacker"], raw_data["defender"],
                                 raw_data["rounds"], library)
        print(str(battle_instance.generate_summary_text()))
        print(f"\nBattle lasted {len(battle_instance.round_results)} rounds.")

    if not one_shot_only and not args.quickrun:
        # execute interpreter
        interp = Interpreter(args.uniconfig, args.shipsconfig)
        log_enable = False
        if args.interpreter_log_enable:
            log_enable = True
        if args.interpreter_preload:
            interp.run(preload_file=args.interpreter_preload, logs_enabled=log_enable)
        else:
            interp.run(logs_enabled=log_enable)

    # one_shot_only is True or interpreter has exited
    print("\nIdleISS exiting")


if __name__ == "__main__":
    run()
