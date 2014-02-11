from collections import namedtuple
from os.path import join, dirname, abspath
import json

ship_schema_fields = ['shield', 'armor', 'hull', 'firepower', 'size',
    'weapon_size', 'multishot', 'sensor_strength',]
ship_schema_optional_fields = ['hullclass', 'buffs', 'debuffs']

buff_effects = ['local_shield_repair', 'local_armor_repair',
    'remote_shield_repair', 'remote_armor_repair',]
# XXX damage will become a debuff.
debuff_effects = ['target_painter', 'tracking_disruption', 'ECM', 'web',]

ShipBuffs = namedtuple('ShipBuffs', buff_effects)

# Dual purpose: in a schema these will be the stats that the ships
# constructed using this schema can potentially apply to targets.
# In a ship, these are the actual debuffs that it is suffering.
ShipDebuffs = namedtuple('ShipDebuffs', debuff_effects)

ShipSchema = namedtuple('ShipSchema', ['name'] + ship_schema_fields +
    ship_schema_optional_fields)

ShipAttributes = namedtuple('ShipAttributes', ['shield', 'armor', 'hull'])

def _construct_tuple(tuple_cls, kwargs, default_value=0):
    """
    Constructs a namedtuple object, using the tuple_cls as the template
    and kwargs as the supplied keyward arguments, which will be merged
    with the default keywords and default_value if the required ones are
    not provided.
    """

    default_kwargs = {f: kwargs.get(f, default_value)
        for f in tuple_cls._fields}
    return tuple_cls(**default_kwargs)

# I don't quite like this method of providing default values, but also
# don't like overloading the __new__ method...
# schema - the full schema.
# attributes - ShipAttributes
# debuffs - debuffs.
_Ship = namedtuple('Ship', ['schema', 'attributes', 'debuffs'])
def Ship(schema, attributes, debuffs=None):
    if not debuffs:
        debuffs = ShipDebuffs(*([False] * len(debuff_effects)))
    return _Ship(schema, attributes, debuffs)


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

        raw_ship_hullclasses = raw_data['sizes'].keys()
        self.ship_data = {}

        for ship_name, data in raw_data['ships'].items():
            missing = self._check_missing_keys('ships', data)
            if missing:
                raise ValueError("%s does not have %s attribute" % (
                    ship_name, ', '.join(missing)))

            updates = {}

            updates['size'] = type(data['size']) != int and \
                                  self.size_data[data['size']] or \
                              data['size']
            updates['weapon_size'] = self.size_data[data['weapon_size']]

            updates['hullclass'] = data.get('hullclass', ship_name)

            updates['buffs'] = _construct_tuple(
                ShipBuffs, data.get('buffs', {}))
            updates['debuffs'] = _construct_tuple(
                ShipDebuffs, data.get('debuffs', {}))

            updates['name'] = ship_name

            # finally merge the updated fields here before constructing
            # final schema object to limit side effects.
            data.update(updates)

            self.ship_data[ship_name] = _construct_tuple(ShipSchema, data)

            # validation for multishot target.
            multishot_list = data['multishot']
            for multishot_target in multishot_list:
                if multishot_target not in raw_ship_hullclasses:
                    raise ValueError(multishot_target + " does not exist as a hullclass")

        self.ordered_ship_data = sorted(self.ship_data.values(),
            key=ship_size_sort_key)

    def get_ship_schemata(self, ship_name):
        return self.ship_data[ship_name]
