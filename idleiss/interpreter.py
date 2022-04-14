from idleiss.core import GameEngine
import time
import re

# all calls from Interpreter should be to idleiss.core.GameEngine
# an external program which imports idleiss should also only make calls to GameEngine

class Interpreter(object):
    def __init__(self, universe_filename, library_filename):
        self.current_time = int(time.time())
        self.engine = GameEngine(universe_filename, library_filename)
        self.init_parser()
        self.userlist = []
        self.is_started = False

    def init_parser(self):
        self.parser_regex = {}
        self.parser_command_list = "Commands: exit|e|q"
        self.add_parser([r"init\s*$"], self.init_engine, "init")
        self.add_parser([r"add\s+(?P<username>.*)\s*$"], self.add_user, "add <username>")
        self.add_parser([r"inc_time\s+(?P<duration>.*)\s*$"], self.increment_time, "inc_time <length>")
        self.add_parser([f"inspect\s+(?P<username>.*)\s*$"], self.inspect, "inspect <username>")
        self.add_parser([f"info\s+(?P<system_name>.*)\s*$"], self.info, "info <system_name>")

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
        return f"core started: events:\n{mes_manager.get_broadcasts_with_time_diff(self.current_time)}"

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
        return f"time incremented by {duration} to {self.current_time}, " \
               f"events:\n{mes_manager.get_broadcasts_with_time_diff(self.current_time)}"

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
