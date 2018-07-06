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
        self.current_time = int(time.time())

    def init_parser(self):
        self.parser_regex = {}
        self.parser_command_list = 'Commands: exit|e|q'
        self.add_parser([r'add\s+(?P<username>.*)\s*$'], self.add_user, 'add <username>')
        self.add_parser([r'inc_time\s+(?P<duration>.*)\s*$'], self.increment_time, 'inc_time <length>')

    def add_parser(self, phrases, callback, help_text):
        self.parser_command_list += ', ' + help_text
        for phrase in phrases:
            self.parser_regex[re.compile(phrase, re.IGNORECASE)] = callback

    def parse(self, command):
        reply = ''
        for result in self.parser_regex.keys():
            match = result.search(command)
            if match:
                if len(reply) != 0:
                    reply += '\n'
                reply += str(self.current_time) + ': ' + self.parser_regex[result](match)
        return reply

    def add_user(self, match):
        username = match.group("username")
        self.engine.user_logged_in(username, self.current_time)
        return 'user ' + username + ' logged in'

    def increment_time(self, match):
        duration = int(match.group("duration"))
        if type(duration) != int:
            return 'error: argument was not an int'
        self.current_time += duration
        return 'time incremented by ' + str(duration) + ' and the following events occurred:\n' + \
               str(self.engine.update_world([], self.current_time))

    def run(self):
        print('')
        print('IdleISS Interpreter: Send commands to IdleISS Core')
        print(self.parser_command_list)
        command = input("> ")
        while not (command == 'exit' or command == 'e' or command == 'q'):
            print(self.parse(command))
            command = input("> ")
