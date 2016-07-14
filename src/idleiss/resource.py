class Location_Already_Exists(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Location_Does_Not_Exist(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ResourceManager(object):
    def __init__(self):
        self.basic_materials = 0
        self.advanced_materials = 0
        self.money = 0
        #income is per second
        self.basic_materials_income = 0
        self.advanced_materials_income = 0
        self.money_income = 0
        self.income_sources = {}
        #income sources are a nested dict of
        # {starsystem:{
        #       location:
        #           [type (moon, station, belt, or other),
        #           basic_income,
        #           adv_income,
        #           money income
        #       ]
        #   }
        #}
        #example:
        #{"START SYSTEM": {
        #   "ISS": ["station", 2, 1, 1]
        #   }
        #}

    def pay_resources(self, seconds):
        self.basic_materials += self.basic_materials_income*seconds
        self.advanced_materials += self.advanced_materials_income*seconds
        self.money += self.money_income*seconds

    def add_income_source(self, system, location, source_type, basic_income,
                          adv_income, money_income):
        if basic_income < 0 or adv_income < 0 or money_income < 0:
            raise ValueError("Income for an income source cannot be negative")

        self.basic_materials_income += basic_income
        self.advanced_materials_income += adv_income
        self.money_income += money_income
        if system in self.income_sources:
            if location in self.income_sources[system]:
                raise Location_Already_Exists(str(location) + "@" + str(system) + " already exists.")
            else:
                self.income_sources[system].update({location: [source_type, basic_income, adv_income, money_income]})
        else:
            self.income_sources.update({system: {location: [source_type, basic_income, adv_income, money_income]}})

    def remove_income_source(self, system, location):
        if system in self.income_sources:
            if location in self.income_sources[system]:
                type, b_i, a_i, m_i = self.income_sources[system][location]
                self.basic_materials_income -= b_i
                self.advanced_materials_income -= a_i
                self.money_income -= m_i
                if self.basic_materials_income < 0 or self.advanced_materials_income < 0 or self.money_income < 0:
                    raise ValueError("Income is negative after removing income source "+str(location)+"@"+str(system)+": " + str(self.basic_materials_income) + " " + str(self.advanced_materials_income) + " " + str(self.money_income))
                self.income_sources[system].pop(location)
                if len(self.income_sources[system]) == 0:
                    self.income_sources.pop(system)
            else:
                raise Location_Does_Not_Exist(str(location)+"@"+str(system)+" does not exist.")
        else:
            raise Location_Does_Not_Exist(str(location)+"@"+str(system)+" does not exist.")

    def update_income_source(self, system, location, basic_income, adv_income, money_income):
        if basic_income < 0 or adv_income < 0 or money_income < 0:
            raise ValueError("Income for an income source cannot be negative")

        if system in self.income_sources:
            if location in self.income_sources[system]:
                type, b_i, a_i, m_i = self.income_sources[system][location]
                self.basic_materials_income += basic_income - b_i
                self.advanced_materials_income += adv_income - a_i
                self.money_income += money_income - m_i
