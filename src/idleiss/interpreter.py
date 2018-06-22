#from idleiss.universe import Universe
#from idleiss.ship import ShipLibrary
from idleiss.core import GameEngine

# all calls from Interpreter should be to idleiss.core.GameEngine
# an external program which imports idleiss should also only make calls to GameEngine

class Interpreter(object):
    def __init__(self, universe_filename, library_filename):
        self.engine = GameEngine(universe_filename, library_filename)
        self.init_parser()

    def init_parser(self):
        self.parser_commands = 'Commands: exit'
        pass

    def parse(self, command):
        pass

    def run(self):
        print('')
        print('IdleISS Interpreter: Send commands to IdleISS Core')
        print(self.parser_commands)
        command = input("> ")
        while not (command == 'exit' or command == 'e'):
            self.parse(command)
            command = input("> ")
