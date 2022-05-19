# IdleISS: The Internet Spaceships IdleRPG

### Setup IdleISS stand-alone for development:
```
$ pip install -e .[dev]
```
### Running the Test Suite
```
$ pytest --runslow
```
### Running the Interpreter to Send Commands to a Default Settings Game Engine
```
$ idleiss
[config file import details displayed here]

IdleISS Interpreter: Send commands to IdleISS Core
Commands: [full list of commands here]
[current timestamp]||
```
Entering some example commands:
```
[current timestamp]||add u1
[current timestamp]: user u1 logged in
[current timestamp]||add u2
[current timestamp]: user u2 logged in
[current timestamp]||init
[current timestamp]: core started: events:
u1 has constructed their first structure, an Outpost in [starting system]. Their journey in the universe begins here.
u2 has constructed their first structure, an Outpost in [starting system]. Their journey in the universe begins here.
[current timestamp]>scan low u1
[current timestamp]: [scan results]
```
### Command Line Help
```
$ idleiss --help

usage: idleiss [-h] [-o] [-q] [-m] [-M] [-u UNICONFIG] [-s SHIPSCONFIG] [-r SCANCONFIG] [-b [SIMBATTLE]] [-p INTERPRETER_PRELOAD] [-l SAVE_FILE]


options:
  -h, --help            show this help message and exit
  -o, --log-interpreter
                        Enable interpreter logs for future playback. Logs are stored in interpreter_log.txt
  -q, --quick           Do not run the interpreter, only verify config files
  -m, --gen-maps        Generate the universe map and the regional maps in output/maps/ then exit
  -M, --gen-all-maps    Generate the universe map, the region maps, and the constellation maps in output/maps/ then exit
  -u UNICONFIG, --universe UNICONFIG
                        Set json universe settings file, if not provided the default config/Universe_Config.json will be used
  -s SHIPSCONFIG, --ships SHIPSCONFIG
                        Set json ships settings file, if not provided the default config/Ships_Config.json will be used
  -r SCANCONFIG, --scanning SCANCONFIG
                        Set json scan settings file, if not provided the default config/Scan_Config.json will be used
  -b [SIMBATTLE], --simulate-battle [SIMBATTLE]
                        Simulate a fleet fight between two fleets using a file and exit. Example file: config/Example_Fleet_Fight.json
  -p INTERPRETER_PRELOAD, --preload INTERPRETER_PRELOAD
                        if the interpreter is executed then this file will be used as the initial commands before control is given to the user
  -l SAVE_FILE, --load-save SAVE_FILE
                        Load GameEngine instance from save file
```
### Using IdleISS with another interface:
Implement an interface similar to interpreter.py's interface to core.py.
An example of a discord impelemntation can be found here: [duskdragon/polyhedra](https://github.com/DuskDragon/polyhedra)
