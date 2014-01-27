from os.path import join, dirname, abspath
import json


class ShipLibrary(object):

    _required_keys = {
        '': ['sizes', 'ships',],  # top level keys
        'ships': ['shield', 'armor', 'hull', 'firepower', 'size',
            'weapon_size', 'multishot',],
    }

    def __init__(self, library_filename=None):
        self.raw_data = None
        if library_filename:
            self.load(library_filename)

    def _check_missing_keys(self, key_id, value):
        """
        value - the dict to be validated
        """

        required_keys = set(self._required_keys[key_id])
        provided_keys = set(value.keys())
        return required_keys - provided_keys

    def load(self, filename):

        with open(filename) as fd:
            self.raw_data = json.load(fd)

        missing = self._check_missing_keys('', self.raw_data)
        if missing:
            raise ValueError(', '.join(missing) + ' not found')

        self.size_data = self.raw_data['sizes']
        self.ship_data = self.raw_data['ships']
        for ship_name in self.ship_data:
            ship = self.ship_data[ship_name]
            missing = self._check_missing_keys('ships', ship)
            if missing:
                raise ValueError("%s does not have %s attribute" % (
                    ship, ', '.join(missing)))

            multishot_list = ship['multishot']
            for multishot_target in multishot_list:
                if multishot_target not in self.ship_data:
                    raise ValueError(multishot_target + " does not exist as a shiptype")
        # log("load succeded")
        self.raw_data = None

    def get_ship_schemata(ship_name):
        return self.ship_data[ship_name]

    # consider deprecating the ones below.

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
