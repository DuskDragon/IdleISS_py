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
        for ship_name in self.ship_data:
            ship = self.ship_data[ship_name]
            if "shield" not in ship:
                raise ValueError(ship_name + " does not have shield attribute")
            if "armor" not in ship:
                raise ValueError(ship_name + " does not have armor attribute")
            if "hull" not in ship:
                raise ValueError(ship_name + " does not have hull attribue")
            if "firepower" not in ship:
                raise ValueError(ship_name + " does not have firepower attribute")
            if "size" not in ship:
                raise ValueError(ship_name + " does not have size attribute")
            if "weapon size" not in ship:
                raise ValueError(ship_name + " does not have weapon size attribute")
            if "multishot" not in ship:
                raise ValueError(ship_name + " does not have multishot attribute")
            multishot_list = ship['multishot']
            for multishot_target in multishot_list:
                if multishot_target not in self.ship_data:
                    raise ValueError(multishot_target + " does not exist as a shiptype")
        # log("load succeded")
        self.raw_data = None

    def ship_shield(self, ship_name):
        return self.ship_data[ship_name]['shield']

    def ship_armor(self, ship_name):
        return self.ship_data[ship_name]['armor']

    def ship_hull(self, ship_name):
        return self.ship_data[ship_name]['armor']

    def ship_firepower(self, ship_name):
        return self.ship_data[ship_name]['firepower']

    def ship_size(self, ship_name):
        return self.ship_data[ship_name]['size']

    def ship_weapon_size(self, ship_name):
        return self.ship_data[ship_name]['weapon size']

    def ship_multishot(self, ship_attacking, ship_target):
        if ship_target not in self.ship_data[ship_attacking]['multishot']:
            return 1
        else:
            return self.ship_data[ship_attacking]['multishot'][ship_target]
