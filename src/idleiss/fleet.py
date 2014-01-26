from os.path import join, dirname, abspath
import json

class ShipLibrary(object):
    def __init__(self, library_filename=None):
        self.raw_data = None
        if library_filename:
            self.load(library_filename)

    def load(self, filename):
        fd = open(filename)
        self.raw_data = json.load(fd)
        fd.close()
        if "sizes" not in self.raw_data:
            raise ValueError("ship sizes not found")
        if "ships" not in self.raw_data:
            raise ValueError("ship data not found")
        self.size_data = self.raw_data['sizes']
        self.ship_data = self.raw_data['ships']

class FleetManager(object):
    def __init__(self):
        pass

class Battle(object):
    def __init__(self, attacker, defender, rounds):
        pass
