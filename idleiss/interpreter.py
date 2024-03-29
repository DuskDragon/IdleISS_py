from idleiss.core import GameEngine
import time
import re
import json
import os
import pathlib
import pprint

from random import Random

# all calls from Interpreter should be to idleiss.core.GameEngine
# an external program which imports idleiss should also only make calls to GameEngine

class Interpreter(object):
    def __init__(self, universe_filename, library_filename, scanning_filename, save_filename=None):
        self.current_time = int(time.time())
        self._load(universe_filename, library_filename, scanning_filename, save_filename)
        self.init_parser()
        self.userlist = []
        self.is_started = False
        self.save_filename = save_filename
        self.pp = pprint.PrettyPrinter(indent=4, width=68, compact=True) #68=80 minus '##########: '

    def _load(self, universe_filename, library_filename, scanning_filename, save_filename):
        save = None
        if save_filename != None:
            savefile = pathlib.Path(save_filename)
            savefile.touch(exist_ok=True)
            if os.path.getsize(save_filename) == 0:
                with open(save_filename, 'w') as fd:
                    fd.write('{}')
                print(f'{save_filename} was not present. Generating fresh IdleISS instance...')
                self.engine = GameEngine(universe_filename, library_filename, scanning_filename, {})
                return
            with open(save_filename, 'r') as fd:
                save = json.load(fd)
            savedata_engine = save.get('engine', None)
            savedata_userlist = save.get('userlist', None)
            if save == {}:
                print(f'{save_filename} was empty. Generating fresh IdleISS instance...')
                self.engine = GameEngine(universe_filename, library_filename, scanning_filename, {})
                return
            if ( #TODO move to validate function and make more robust
                    savedata_engine == None or
                    savedata_userlist == None
                ):
                raise RuntimeError(f'{save_filename} contains invalid save data, delete the file or replace with valid save data to continue.')
            self.engine = GameEngine(universe_filename, library_filename, scanning_filename, savedata_engine)
            self.userlist = savedata_userlist
            print(f"Current time is {self.current_time}, save has: {savedata_engine['world_timestamp']}")
            self.current_time = max(savedata_engine["world_timestamp"], self.current_time)
            print(f"Current time forced to {self.current_time}")
            print(f'Successfully loaded savefile: {save_filename}')
        else:
            print(f'No save file provided. Generating fresh IdleISS instance...')
            self.engine = GameEngine(universe_filename, library_filename, scanning_filename, {})

    def init_parser(self):
        self.parser_regex = {}
        self.parser_command_list = "Commands: exit|e|q"
        self.add_parser([r"init\s*$"], self.init_engine, "init")
        self.add_parser([r"add\s+(?P<username>\w+)\s*$"], self.add_user, "add <username>")
        self.add_parser([r"inc_time\s+(?P<duration>\w+)\s*$"], self.increment_time, "inc_time <length>")
        self.add_parser([r"inspect\s+(?P<username>\w+)\s*$"], self.inspect, "inspect <username>")
        self.add_parser([r"info\s+(?P<system_name>\w+)\s*$"], self.info, "info <system_name>")
        self.add_parser([r"scan\s+(?P<type>\w+)\s+(?P<username>\w+)\s*(?P<pos>\w+)?\s*$"], self.scan, "scan <type> <username> [<pos>]")
        self.add_parser([r"destinations\s+(?P<username>\w+)\s*$"], self.destinations, "destinations <username>")
        self.add_parser([r"save\s*(?P<filename>[a-zA-Z0-9_]+.[a-zA-Z0-9_]+)?\s*$"], self.save, "save [<filename>]")

    def add_parser(self, phrases, callback, help_text):
        self.parser_command_list += f", {help_text}"
        for phrase in phrases:
            self.parser_regex[re.compile(phrase, re.IGNORECASE)] = callback

    def parse(self, command):
        reply_array = []
        for result in self.parser_regex.keys():
            match = result.search(command)
            if match:
                if len(reply_array) != 0:
                    reply_array.append("\n")
                reply_array.append(f"{self.current_time}: {self.parser_regex[result](match)}")
        if len(reply_array) == 0:
            return self.parser_command_list
        return "".join(reply_array)

    def init_engine(self, match):
        if self.is_started:
            return "error: init already done"
        self.is_started = True
        mes_manager = self.engine.update_world(self.userlist, self.current_time)
        message_array = mes_manager.get_broadcasts_with_time_diff(self.current_time)
        updates = '\n'.join(message_array)
        return f"core started: events:\n{updates}"

    def add_user(self, match):
        username = match.group("username")
        if username not in self.userlist:
            self.userlist.append(username)
        return f"user {username} logged in"

    def increment_time(self, match):
        if not self.is_started:
            return "error: use init first"
        duration = int(match.group("duration"))
        if type(duration) != int:
            return "error: duration was not an int"
        if duration < 1:
            return "error: duration must be positive integer"
        self.current_time += duration
        mes_manager = self.engine.update_world(self.userlist, self.current_time)
        message_array = mes_manager.get_broadcasts_with_time_diff(self.current_time)
        updates = '\n'.join(message_array)
        return f"time incremented by {duration} to {self.current_time}, " \
               f"events:\n{updates}"

    def inspect(self, match):
        if not self.is_started:
            return "error: use init first"
        username = match.group("username")
        return self.engine.inspect_user(username)

    def info(self, match):
        if not self.is_started:
            return "error: use init first"
        system_name = match.group("system_name")
        return self.engine.info_system(system_name)

    def scan(self, match):
        if not self.is_started:
            return "error: use init first"
        username = match.group("username")
        type = match.group("type")
        pos = match.group("pos")
        if type not in ["low", "focus", "high", "l", "f", "h"]:
            return f"error: incorrect scan type entered: {type}. Use: [l]ow, [f]ocus, or [h]igh"
        if type == "f" or type == "focus":
            if pos == None:
                return f"error: for scan type {type} a pos value is needed"
            else:
                pos = int(pos)
                sel_y = int((pos-1)/self.engine.scanning.settings.focus_height_max)
                sel_x = int(pos-(sel_y*self.engine.scanning.settings.focus_width_max))
                mess, grid = self.engine.scan(Random(), self.current_time, username, type, (pos,sel_x,sel_y))
                full_mess = f"{mess}\nFrequency Map:\n{self.pp.pformat(grid)}"
                return full_mess
        return self.engine.scan(Random(), self.current_time, username, type)[0]

    def destinations(self, match):
        if not self.is_started:
            return "error: use init first"
        username = match.group("username")
        strs = self.engine.user_destinations(self.current_time, username, 2000, 3)
        total = ""
        for str in strs:
            total += str
            total += "\n--------------\nEnd of Message\n"
        total = total[0:-1]
        return total

    def save(self, match):
        save_file = None
        if match.group("filename") == None:
            if self.save_filename == None:
                return f"error: save needs filename when idleiss not started with -l"
            else:
                save_file = self.save_filename
        else:
            save_file = match.group("filename")
        engine_savedata = self.engine.generate_savedata()
        savedata = {
            'engine': engine_savedata,
            'userlist': self.userlist,
        }
        #verify that dump doesn't fail before writing
        testout = json.dumps(savedata, indent=4)
        with open(save_file, 'w') as fd:
            fd.write(testout)
        return f"savefile generated in file: {save_file} at {self.current_time}"

    def run(self, preload_file=None, logs_enabled=False):
        if logs_enabled:
            log_fd = open("interpreter_log.txt", "w")
        print("")
        print("IdleISS Interpreter: Send commands to IdleISS Core")
        print(self.parser_command_list)

        # check for preloaded commands
        if preload_file:
            with open(preload_file) as preload_fd:
                for raw_line in preload_fd:
                    line = raw_line.rstrip()
                    if not self.is_started:
                        print(f"{self.current_time}||{line}")
                    else:
                        print(f"{self.current_time}> {line}")
                    if logs_enabled:
                        log_fd.write(f"{line}\n")
                    if line == "exit" or line == "e" or line == "q":
                        return
                    print(self.parse(line))

        # switch to user control
        if not self.is_started:
            command = input(f"{self.current_time}||")
        else:
            command = input(f"{self.current_time}> ")
        while not (command == "exit" or command == "e" or command == "q"):
            if logs_enabled:
                log_fd.write(f"{command}\n")
            print(self.parse(command))
            if not self.is_started:
                command = input(f"{self.current_time}||")
            else:
                command = input(f"{self.current_time}> ")

        if logs_enabled:
            log_fd.close()
