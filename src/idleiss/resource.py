

class ResourceManager(object):
    def __init__(self):
        self.basic_materials = 0
        self.advanced_materials = 0
        self.money = 0
        #income is per second
        self.basic_materials_income = 0
        self.advanced_materials_income = 0
        self.money_income = 0
        
    def pay_resources(self, seconds):
        self.basic_materials += self.basic_materials_income*seconds
        self.advanced_materials += self.advanced_materials_income*seconds
        self.money += self.money_income*seconds
