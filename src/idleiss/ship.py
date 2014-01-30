from collections import namedtuple
from os.path import join, dirname, abspath
import json


ship_schema_fields = ['shield', 'armor', 'hull', 'firepower', 'size',
    'weapon_size', 'multishot',]
ShipSchema = namedtuple('ShipSchema', ['name'] + ship_schema_fields)

Ship = namedtuple('Ship', ['schema', 'attributes'])
# schema - the full schema.
# attributes - ShipAttributes

ShipAttributes = namedtuple('ShipAttributes', ['shield', 'armor', 'hull',])


class ShipLibrary(object):

    _required_keys = {
        '': ['sizes', 'ships',],  # top level keys
        'ships': ship_schema_fields,
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

    def get_ship_schemata(self, ship_name):
        return ShipSchema(ship_name, **self.ship_data[ship_name])
