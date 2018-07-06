#from idleiss.universe import Universe
#from idleiss.ship import ShipLibrary
from idleiss.core import GameEngine
import time
import re

# all calls from Interpreter should be to idleiss.core.GameEngine
# an external program which imports idleiss should also only make calls to GameEngine

class Interpreter(object):
    def __init__(self, universe_filename, library_filename):
        self.engine = GameEngine(universe_filename, library_filename)
        self.init_parser()

    def init_parser(self):
        self.parser_regex = {}
        self.parser_command_list = 'Commands: exit|e|q'
        self.add_parser([r'add\s+(?P<username>.*)\s*$'], self.add_user, 'add <username>')

    def add_parser(self, phrases, callback, help_text):
        self.parser_command_list += ', ' + help_text
        for phrase in phrases:
            self.parser_regex[re.compile(phrase, re.IGNORECASE)] = callback

    def parse(self, command, timestamp):
        reply = ''
        for result in self.parser_regex.keys():
            match = result.search(command)
            if match:
                if len(reply) != 0:
                    reply += '\n'
                reply += str(timestamp) + ': ' + self.parser_regex[result](match, timestamp)
        return reply

    def add_user(self, match, timestamp):
        username = match.group("username")
        self.engine.user_logged_in(username, timestamp)
        return 'user ' + username + ' logged in'

    def run(self):
        print('')
        print('IdleISS Interpreter: Send commands to IdleISS Core')
        print(self.parser_command_list)
        command = input("> ")
        while not (command == 'exit' or command == 'e' or command == 'q'):
            print(self.parse(command, int(time.time())))
            command = input("> ")
