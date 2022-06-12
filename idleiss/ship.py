from collections import namedtuple
from os.path import join, dirname, abspath
import json

ship_schema_fields = ["hullclass", "shield", "armor", "hull", "weapons", "size", "sensor_strength", "cost"]
ship_schema_optional_fields = ["buffs", "debuffs", "sortclass", "is_structure", "ecm_immune"]

structure_schema_fields = ["produces", "reinforce_cycles", "structure_tier", "shipyard", "security", "sov_structure"]

buff_effects = ["local_shield_repair", "local_armor_repair",
    "remote_shield_repair", "remote_armor_repair",]
# XXX damage may become a debuff.
debuff_effects = ["target_painter", "tracking_disruption", "ECM", "web",]

ShipBuffs = namedtuple("ShipBuffs", buff_effects)


# In a ship, these are the actual debuffs that it is suffering.
# weapons will have debuff_effects on them that can apply these effects
ShipDebuffs = namedtuple("ShipDebuffs", debuff_effects)

ShipSchema = namedtuple("ShipSchema", ["name"] + ship_schema_fields +
    ship_schema_optional_fields)

StructureSchema = namedtuple("StructureSchema", ["name"] + structure_schema_fields)

ShipAttributes = namedtuple("ShipAttributes", ["shield", "armor", "hull"])

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
_Ship = namedtuple("Ship", ["schema", "attributes", "debuffs"])
def Ship(schema, attributes, debuffs=None):
    if not debuffs:
        debuffs = ShipDebuffs(*([False] * len(debuff_effects)))
    return _Ship(schema, attributes, debuffs)

class ShipLibrary(object):

    _required_keys = {
        "": ["sizes", "hullclasses", "ships", "structures"],  # top level keys
        "ships": ship_schema_fields,
        "structures": structure_schema_fields + ship_schema_fields,
    }
    # Optional top level keys: "sortclasses"

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
        self.starting_structure = None
        self.sov_structure = None
        missing = self._check_missing_keys("", raw_data)
        if missing:
            raise ValueError(", ".join(missing) + " not found")

        self.size_data = {}
        self.size_data.update(raw_data["sizes"])

        self.hullclasses_data = raw_data["hullclasses"]
        if raw_data.get("sortclasses", None) != None:
            self.sortclasses_exists = True
            self.sortclasses_data = raw_data["sortclasses"]
        else:
            self.sortclasses_exists = False
            self.sortclasses_data = self.hullclasses_data
        self.ship_data = {}
        self.structure_data = {}

        # verify "structures" and "ships" have no name conflicts:
        if len(set(raw_data["ships"].keys()).intersection(set(raw_data["structures"].keys()))) != 0:
            raise ValueError(f"ships and structures have an item with the same name:\n"
                             f"{set(raw_data['ships'].keys()).intersection(set(raw_data['structures'].keys()))}")

        # verify that only one starting structure exists (tier:0)
        for structure_name, data in raw_data["structures"].items():
            if data["structure_tier"] == 0:
                if self.starting_structure == None:
                    self.starting_structure = raw_data["structures"][structure_name]
                else:
                    raise ValueError(f"{structure_name}: second structure with 'structure_tier' = 0 found, only one starting structure can exist")
        # verify that only one sov_structure exists ("sov_structure" = true)
        for structure_name, data in raw_data["structures"].items():
            if data.get("sov_structure", False) == True:
                if self.sov_structure == None:
                    self.sov_structure = raw_data["structures"][structure_name]
                else:
                    raise ValueError(f"{structure_name}: second structure with 'sov_structure' = true found, only one sov_structure can exist")

        # tag all structures as structures before merging into ships:
        for structure_name, data in raw_data["structures"].items():
            data["is_structure"] = True
            data["ecm_immune"] = True

        # tag all ships as not structures:
        for ship_name, data in raw_data["ships"].items():
            data["is_structure"] = False

        # merge "structures" and "ships" since they need to be treated as ships in combat
        ships_and_structures = {**raw_data["ships"], **raw_data["structures"]}

        for ship_name, data in ships_and_structures.items():
            missing = self._check_missing_keys("ships", data)
            if missing:
                raise ValueError(f"{ship_name} does not have {', '.join(missing)} attribute")

            updates = {}

            #apply weapon_size adjustment to each weapon
            updates["weapons"] = []
            for v in data["weapons"]:
                if not isinstance(v["weapon_size"], int):
                    v["weapon_size"] = self.size_data[v["weapon_size"]]
                v["area_of_effect"] = v.get("area_of_effect", 1)
                v["cycle_time"] = v.get("cycle_time", 1)
                updates["weapons"].append(v)

            size_type = type(data["size"])
            updates["size"] = data["size"] if size_type is int else self.size_data[data["size"]]

            if data["hullclass"] not in self.hullclasses_data:
                raise ValueError(f"{ship_name}: hullclass {data['hullclass']} not in hullclasses")
            if self.sortclasses_exists:
                if data["sortclass"] not in self.sortclasses_data:
                    raise ValueError(f"{ship_name}: sortclass {data['sortclass']} not in sortclasses")
                updates["sortclass"] = data["sortclass"]
            else: #False = self.sortclasses_exists
                updates["sortclass"] = data["hullclass"]

            #convert sortclass to a number based on the position of the string in the array sortclasses
            updates["sortclass"] = self.sortclasses_data.index(updates["sortclass"])

            updates["buffs"] = _construct_tuple(ShipBuffs, data.get("buffs", {}))
            updates["debuffs"] = _construct_tuple(ShipDebuffs, data.get("debuffs", {}))

            updates["name"] = ship_name

            valid_cost_types = ["money", "basic_materials", "advanced_materials"]
            # verify "cost" contains: money, basic_materials, and advanced_materials
            for cost_type in valid_cost_types:
                if data["cost"].get(cost_type, None) == None:
                    raise ValueError(f"{ship_name} cost attribue does not contain {cost_type} attribute")

            # validation for weapon systems
            weapons_list = data["weapons"]
            if type(weapons_list) != list:
                raise ValueError(f"{ship_name} weapons attribute is not a list.")
            for weapon in weapons_list:
                if type(weapon) != dict:
                    raise ValueError(f"{ship_name} weapon in weapon_list is not a dictionary")
                if type(weapon["weapon_name"]) != str:
                    raise ValueError(f"{ship_name} weapon_name in weapon_list has invalid name")
                weapon_name = weapon["weapon_name"]
                if type(weapon["weapon_size"]) != int:
                    raise ValueError(f"{ship_name}: {weapon_name}: weapon_size in weapon_list is invalid")
                if type(weapon["firepower"]) != int:
                    raise ValueError(f"{ship_name}: {weapon_name}: firepower in weapon_list is invalid")
                if type(weapon.get("area_of_effect",1)) != int or weapon.get("area_of_effect",1) < 1:
                    raise ValueError(f"{ship_name}: {weapon_name} area_of_effect is invalid (not an integer or less than 1)")
                if type(weapon["cycle_time"]) != int or weapon.get("cycle_time",1) < 1:
                    raise ValueError(f"{ship_name}: {weapon_name} cycle_time is invalid (not an integer or less than 1)")
                # validation for priority targets.
                priority_list = weapon.get("priority_targets", 0)
                if type(priority_list) != list:
                    raise ValueError(f"{ship_name}: {weapon_name}: priority_targets attribute is not a list")
                for priority_level in priority_list:
                    if priority_level == []:
                        raise ValueError(f"{ship_name}: {weapon_name}: cannot have empty level in priority_list array")
                    for priority_target in priority_level:
                        if priority_target not in self.hullclasses_data:
                            raise ValueError(f"{ship_name}: {weapon_name}: {priority_target} does not exist as a hullclass or category")
            # end of massive weapon_list for loop
            # finally merge the updated fields here before constructing

            if "ecm_immune" in data.keys():
                if type(data["ecm_immune"]) != bool:
                    raise ValueError(f"{ship_name}: ecm_immune attribute is not a boolean")
            else:
                updates["ecm_immune"] = False

            # Structure attributes check
            if "is_structure" in data.keys():
                if type(data["is_structure"]) != bool:
                    raise ValueError(f"{ship_name}: is_structure attribute is not a boolean")
            else:
                updates["is_structure"] = False
            # Structure specific attributes
            if data.get("is_structure", False):
                missing = self._check_missing_keys("structures", data)
                if missing:
                    raise ValueError(f"{ship_name} does not have {', '.join(missing)} attribute")

                # add to structure_data
                self.structure_data[ship_name] = _construct_tuple(StructureSchema, data)

            # final schema object to limit side effects.
            data.update(updates)
            self.ship_data[ship_name] = _construct_tuple(ShipSchema, data)
        # end for loop: ship_name, data in ships_and_structures.items():

        self.ordered_ship_data = sorted(self.ship_data.values(), key=lambda s: s.sortclass)
        # verify that we have loaded a starting_structure
        if self.starting_structure == None:
            raise ValueError("_load: ship config file does not contain a starting structure with structure_tier = 0")

    def get_ship_schemata(self, ship_name):
        return self.ship_data[ship_name]
