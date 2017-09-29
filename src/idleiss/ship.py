from collections import namedtuple
from os.path import join, dirname, abspath
import json

ship_schema_fields = ['hullclass', 'shield', 'armor', 'hull', 'weapons', 'size',
    'priority_targets', 'sensor_strength',]
ship_schema_optional_fields = ['buffs', 'debuffs']

buff_effects = ['local_shield_repair', 'local_armor_repair',
    'remote_shield_repair', 'remote_armor_repair',]
# XXX damage may become a debuff.
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
        '': ['sizes', 'hullclasses', 'ships',],  # top level keys
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

        self.hullclasses_data = raw_data['hullclasses']
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

            #apply weapon_size adjustment to each weapon
            updates['weapons'] = []
            for x in range(len(data['weapons'])):
                updates['weapons'].append(data['weapons'][x])
                size_of_weapon = updates['weapons'][x]['weapon_size']
                updates['weapons'][x]['weapon_size'] = type(size_of_weapon) != int and \
                                     self.size_data[size_of_weapon] or \
                                     size_of_weapon

            #updates['hullclass'] = data['hullclass']

            updates['buffs'] = _construct_tuple(
                ShipBuffs, data.get('buffs', {}))
            updates['debuffs'] = _construct_tuple(
                ShipDebuffs, data.get('debuffs', {}))

            updates['name'] = ship_name

            # finally merge the updated fields here before constructing
            # final schema object to limit side effects.
            data.update(updates)

            self.ship_data[ship_name] = _construct_tuple(ShipSchema, data)

            # validation for priority targets.
            priority_list = data['priority_targets']
            if type(priority_list) != list:
                raise ValueError(ship_name+"priority_targets attribute is not a list")
            for priority_level in priority_list:
                if priority_level == []:
                    raise ValueError(ship_name + " cannot have empty level in priority_list array")
                for priority_target in priority_level:
                    if priority_target not in self.hullclasses_data:
                        raise ValueError(ship_name+": "+str(priority_target)+" does not exist as a hullclass")

            # validation for weapon systems
            weapons_list = data['weapons']
            if type(weapons_list) != list:
                raise ValueError(ship_name+" weapons attribute is not a list.")
            for weapon in weapons_list:
                if type(weapon) != dict:
                    raise ValueError(ship_name+" weapon in weapon_list is not a dictionary")
                if type(weapon['weapon_name']) != str:
                    raise ValueError(ship_name+" weapon_name in weapon_list has invalid name")
                if type(weapon['weapon_size']) != int:
                    raise ValueError(ship_name+" weapon_size in weapon_list is invalid")
                if type(weapon['firepower']) != int:
                    raise ValueError(ship_name+" firepower in weapon_list is invalid")



        self.ordered_ship_data = sorted(self.ship_data.values(),
            key=ship_size_sort_key)

    def get_ship_schemata(self, ship_name):
        return self.ship_data[ship_name]
