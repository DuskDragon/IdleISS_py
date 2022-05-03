from collections import namedtuple
import json

site_schema_fields = ["low_chance", "focus_height", "focus_width",
    "high_chance", "quality", "initial_description", "arrival_message",
    "duration", "success_rate", "completion_message", "basic_materials_reward",
    "advanced_materials_reward", "money_reward", "failure_message", "shared"]
site_schema_optional_fields = ["ships", "in_progress_low_chance",
    "in_progress_focus_height", "in_progress_focus_width",
    "in_progress_high_chance"]

setting_schema_fields = ["low_recharge", "focus_recharge", "high_recharge",
    "focus_height_max", "focus_width_max", "max_quality_per_constellation",
    "site_decay"]
setting_schema_optional_fields = []

SiteSchema = namedtuple("SiteSchema", ["name"] + site_schema_fields +
    site_schema_optional_fields)

SettingSchema = namedtuple("SettingSchema", setting_schema_fields +
    setting_schema_optional_fields)

def _construct_tuple(tuple_cls, kwargs, default_value=None): #default is different than in ship.py
    """
    Constructs a namedtuple object, using the tuple_cls as the template
    and kwargs as the supplied keyward arguments, which will be merged
    with the default keywords and default_value if the required ones are
    not provided.
    """

    default_kwargs = {f: kwargs.get(f, default_value)
        for f in tuple_cls._fields}
    return tuple_cls(**default_kwargs)

_Site = namedtuple("Site", ["schema", "attributes"])
def Site(schema, attributes):
    return _Site(schema, attributes)

class Scanning(object):

    _required_keys = {
        "": ["settings", "sites"], # top level keys
        "settings": setting_schema_fields,
        "sites": site_schema_fields
    }

    def __init__(self, config_file, ship_library):
        self.library = ship_library
        self._load(config_file)

    def _check_missing_keys(self, key_id, value):
        """
        value - the dict to be validated
        """
        required_keys = set(self._required_keys[key_id])
        provided_keys = set(value.keys())
        return required_keys - provided_keys

    def _load(self, filename):
        """
        validation funtion which also stores the valid settings and sites
        """
        with open(filename) as fd:
            raw_data = json.load(fd)
        missing = self._check_missing_keys("", raw_data)
        if missing:
            raise ValueError(", ".join(missing) + " not found")
        missing = self._check_missing_keys("settings", raw_data["settings"])
        if missing:
            raise ValueError(", ".join(missing) + " not found")
        for k,v in raw_data["settings"].items():
            if type(v) != int:
                raise ValueError(f'{k} is expected to be an integer, it is a {type(v)}')
        self.settings = _construct_tuple(SettingSchema, raw_data["settings"])
        self.site_data = {}
        for site_name, data in raw_data["sites"].items():
            #check all required keys exist
            missing = self._check_missing_keys("sites", data)
            if missing:
                raise ValueError(", ".join(missing) + " not found")
            #special validation for optional ships listing
            if data.get("ships", {}) != {}:
                for ship, count in data["ships"].items():
                    if count < 0:
                        raise ValueError(f"_load: site config file contains negative ship counts for {ship}")
                    try:
                        self.library.get_ship_schemata(ship)
                    except KeyError as err:
                        raise KeyError(f"_load: site config file contains an invalid ship: {ship} which is not present in ship config file.")
            #required settings validation
            if data["low_chance"] > 1.0 and data["low_chance"] < 0:
                raise ValueError(f"_load: site config file contains invalid 'low_chance' for site: {site_name}. Limits are [0, 1] (inclusive)")
            if data["focus_height"] > self.settings.focus_height_max:
                raise ValueError(f"_load: site config file contains invalid 'focus_height' for site {site_name}. Limits are [1, {self.settings.focus_height_max}] (inclusive, high limit is configurable under 'settings':'focus_height_max')")
            if data["focus_width"] > self.settings.focus_width_max:
                raise ValueError(f"_load: site config file contains invalid 'focus_width' for site {site_name}. Limits are [1, {self.settings.focus_width_max}] (inclusive, high limit is configurable under 'settings':'focus_width_max')")
            if data["high_chance"] > 1.0 and data["high_chance"] < 0:
                raise ValueError(f"_load: site config file contains invalid 'high_chance' for site: {site_name}. Limits are [0, 1] (inclusive)")
            if data["quality"] > self.settings.max_quality_per_constellation:
                raise ValueError(f"_load: site config file contains invalid 'quality' for site {site_name}. Limits are [1, {self.settings.max_quality_per_constellation}] (inclusive, high limit is configurable under 'settings':'max_quality_per_constellation')")
            if type(data["initial_description"]) != str:
                raise ValueError(f"_load: site config file contains invalid 'initial_description' for site {site_name}. Type must be str.")
            if type(data["arrival_message"]) != str:
                raise ValueError(f"_load: site config file contains invalid 'arrival_message' for site {site_name}. Type must be str.")
            if type(data["duration"]) != int:
                raise ValueError(f"_load: site config file contains invalid 'duration' for site {site_name}. Type must be int.")
            if data["success_rate"] > 1.0 and data["success_rate"] < 0:
                raise ValueError(f"_load: site config file contains invalid 'success_rate' for site {site_name}. Limits are [0, 1] (inclusive)")
            if type(data["completion_message"]) != str:
                raise ValueError(f"_load: site config file contains invalid 'completion_message' for site {site_name}. Type must be str.")
            if type(data["basic_materials_reward"]) != int:
                raise ValueError(f"_load: site config file contains invalid 'basic_materials_reward' for site {site_name}. Type must be int.")
            if type(data["advanced_materials_reward"]) != int:
                raise ValueError(f"_load: site config file contains invalid 'advanced_materials_reward' for site {site_name}. Type must be int.")
            if type(data["money_reward"]) != int:
                raise ValueError(f"_load: site config file contains invalid 'money_reward' for site {site_name}. Type must be int.")
            if type(data["failure_message"]) != str:
                raise ValueError(f"_load: site config file contains invalid 'failure_message' for site {site_name}. Type must be str.")
            if data["shared"] != True and data["shared"] != False:
                raise ValueError(f"_load: site config file contains invalid 'shared' for site {site_name}. Type must be true or false.")
            #optional items:
            temp = data.get("in_progress_low_chance", 0)
            if temp > 1.0 and temp < 0:
                raise ValueError(f"_load: site config file contains invalid 'in_progress_low_chance' for site {site_name}. Limits are [0, 1] (inclusive)")
            temp = data.get("in_progress_focus_height", 0)
            if temp > self.settings.focus_height_max and temp < 0:
                raise ValueError(f"_load: site config file contains invalid 'in_progress_focus_height' for site {site_name}. Limits are [1, {self.settings.focus_height_max}] (inclusive, high limit is configurable under 'settings':'focus_height_max')")
            temp = data.get("in_progress_focus_width", 0)
            if temp > self.settings.focus_width_max and temp < 0:
                raise ValueError(f"_load: site config file contains invalid 'in_progress_focus_width' for site {site_name}. Limits are [1, {self.settings.focus_width_max}] (inclusive, high limit is configurable under 'settings':'focus_width_max')")
            temp = data.get("in_progress_high_chance", 0)
            if temp > 1.0 and temp < 0:
                raise ValueError(f"_load: site config file contains invalid 'in_progress_high_chance' for site {site_name}. Limits are [0, 1] (inclusive)")
            #include name in namedtuple object
            data["name"] = site_name
            self.site_data[site_name] = _construct_tuple(SiteSchema, data)

    def get_site_schemata(self, site_name):
        return self.site_data[site_name]

    def generate_constellation_scannables(self, system_count, rand):
        """
        returns an list of size system_count where each list contains a list
        of the sites to be added to the corresponding system
        requires random to be passed to the constructor of this object
        when it was created
        """
        pass
        #current_quality = 0
        #while current_quality < self.settings.max_quality_per_constellation:
        #    self.site_data[