from collections import namedtuple
from os.path import join, dirname, abspath
import json


ship_schema_fields = ['shield', 'armor', 'hull', 'firepower', 'size',
    'weapon_size', 'multishot', 'sensor_strength',]
ship_optional_fields = ['shield_recharge', 'armor_local_repair',
    'remote_shield', 'remote_armor', 'target_painter', 'tracking_disruption',
    'ECM', 'web',]
ShipSchema = namedtuple('ShipSchema', ['name'] + ship_schema_fields +
    ship_optional_fields)

# I don't quite like this method of providing default values, but also
# don't like overloading the __new__ method...
# schema - the full schema.
# attributes - ShipAttributes
# debuffs - debuffs.
_Ship = namedtuple('Ship', ['schema', 'attributes', 'debuffs'])
def Ship(schema, attributes, debuffs=None):
    if not debuffs:
        debuffs = {'active': {}, 'inactive': {}}
    return _Ship(schema, attributes, debuffs)

ShipAttributes = namedtuple('ShipAttributes', ['shield', 'armor', 'hull'])


def ship_size_sort_key(obj):
    return obj.size


class ShipLibrary(object):

    _required_keys = {
        '': ['sizes', 'ships',],  # top level keys
        'ships': ship_schema_fields,
    }

    def __init__(self, library_filename=None):
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
            raw_data = json.load(fd)

        self._load(raw_data)

    def _load(self, raw_data):
        missing = self._check_missing_keys('', raw_data)
        if missing:
            raise ValueError(', '.join(missing) + ' not found')

        self.size_data = {}
        self.size_data.update(raw_data['sizes'])

        raw_ship_names = raw_data['ships'].keys()
        self.ship_data = {}

        for ship_name, data in raw_data['ships'].items():
            missing = self._check_missing_keys('ships', data)
            if missing:
                raise ValueError("%s does not have %s attribute" % (
                    ship_name, ', '.join(missing)))

            data['size'] = self.size_data[data['size']]
            data['weapon_size'] = self.size_data[data['weapon_size']]

            #going to want to depreciate these in the future
            data['shield_recharge'] = data.get('shield_recharge', data['shield'])
            data['armor_local_repair'] = data.get('armor_local_repair', 0)
            data['remote_shield'] = data.get('remote_shield', 0)
            data['remote_armor'] = data.get('remote_shield', 0)
            data['target_painter'] = data.get('target_painter', 0)
            data['tracking_disruption'] = data.get('tracking_disruption', 0)
            data['ECM'] = data.get('ECM', 0)
            data['web'] = data.get('web', 0)

            self.ship_data[ship_name] = ShipSchema(ship_name, **data)

            multishot_list = data['multishot']
            for multishot_target in multishot_list:
                if multishot_target not in raw_ship_names:
                    raise ValueError(multishot_target + " does not exist as a shiptype")

        self.ordered_ship_data = sorted(self.ship_data.values(),
            key=ship_size_sort_key)

    def get_ship_schemata(self, ship_name):
        return self.ship_data[ship_name]
