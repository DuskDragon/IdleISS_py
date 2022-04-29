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
    def __init__(self, savedata=None):
        if savedata == None:
            self.basic_materials = 0
            self.advanced_materials = 0
            self.money = 0
            #income is per second
            self.basic_materials_income = 0
            self.advanced_materials_income = 0
            self.money_income = 0
            self.income_sources = {}
            #income sources are a nested dict of
            # {
            #   starsystem:{
            #       'structure': [
            #           basic_income,
            #           adv_income,
            #           money income
            #       ]
            #    }
            # }
            #
            #example:
            #{"START SYSTEM": {
            #   "ISS": ["station", 2, 1, 1]
            #   }
            #}
            return
        #TODO add validation
        self.basic_materials = savedata['basic_materials']
        self.advanced_materials = savedata['advanced_materials']
        self.money = savedata['money']
        self.basic_materials_income = savedata['basic_materials_income']
        self.advanced_materials_income = savedata['advanced_materials_income']
        self.money_income = savedata['money_income']
        self.income_sources = savedata['income_sources']

    def __str__(self):
        outstr = f"""\
resources: [{self.basic_materials}, {self.advanced_materials}, {self.money}]
\tincome: [{self.basic_materials_income}, {self.advanced_materials_income}, {self.money_income}]
\tsources: {self.income_sources}"""
        return outstr

    def generate_savedata(self):
        save = {
            'basic_materials': self.basic_materials,
            'advanced_materials': self.advanced_materials,
            'money': self.money,
            'basic_materials_income': self.basic_materials_income,
            'advanced_materials_income': self.advanced_materials_income,
            'money_income': self.money_income,
            'income_sources': self.income_sources,
        }
        return save

    def can_afford(self, money, basic, advanced):
        return money <= self.money and basic <= self.basic_materials and advanced <= self.advanced_materials

    def spend(self, money, basic, advanced):
        if not self.can_afford(money, basic, advanced):
            return False
        self.basic_materials -= basic
        self.advanced_materials -= advanced
        self.money -= money
        return True

    def one_time_income(self, money, basic, advanced):
        self.basic_materials += basic
        self.advanced_materials += advanced
        self.money += money

    def produce_income(self, seconds):
        self.basic_materials += self.basic_materials_income*seconds
        self.advanced_materials += self.advanced_materials_income*seconds
        self.money += self.money_income*seconds

    def add_income_source(self, system_name, structure_name, basic_income,
                          adv_income, money_income):
        if basic_income < 0 or adv_income < 0 or money_income < 0:
            raise ValueError("Income for an income source cannot be negative")

        self.basic_materials_income += basic_income
        self.advanced_materials_income += adv_income
        self.money_income += money_income
        if system_name in self.income_sources:
            if structure_name in self.income_sources[system_name]:
                raise Location_Already_Exists(f"{structure_name}@{system_name} already exists.")
            else:
                self.income_sources[system_name].update({structure_name: [basic_income, adv_income, money_income]})
        else:
            self.income_sources.update({system_name: {structure_name: [basic_income, adv_income, money_income]}})

    def remove_income_source(self, system_name, structure_name):
        if system_name in self.income_sources:
            if structure_name in self.income_sources[system_name]:
                b_i, a_i, m_i = self.income_sources[system_name][structure_name]
                self.basic_materials_income -= b_i
                self.advanced_materials_income -= a_i
                self.money_income -= m_i
                if self.basic_materials_income < 0 or self.advanced_materials_income < 0 or self.money_income < 0:
                    raise ValueError(f"Income is negative after removing income source {structure_name}@{system_name}: {self.basic_materials_income} {self.advanced_materials_income} {self.money_income}")
                self.income_sources[system_name].pop(structure_name)
                if len(self.income_sources[system_name]) == 0:
                    self.income_sources.pop(system_name)
            else:
                raise Location_Does_Not_Exist(f"{structure_name}@{system_name} does not exist.")
        else:
            raise Location_Does_Not_Exist(f"{structure_name}@{system_name} does not exist.")

    def update_income_source(self, system_name, structure_name, basic_income, adv_income, money_income):
        if basic_income < 0 or adv_income < 0 or money_income < 0:
            raise ValueError("Income for an income source cannot be negative")

        if system_name in self.income_sources:
            if structure_name in self.income_sources[system_name]:
                b_i, a_i, m_i = self.income_sources[system_name][structure_name]
                self.basic_materials_income += basic_income - b_i
                self.advanced_materials_income += adv_income - a_i
                self.money_income += money_income - m_i
            else:
                raise Location_Does_Not_Exist(f"{structure_name}@{system_name} does not exist.")
        else:
            raise Location_Does_Not_Exist(f"{structure_name}@{system_name} does not exist.")
