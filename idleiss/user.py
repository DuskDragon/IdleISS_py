from .fleet import FleetManager
from .resource import ResourceManager

class User(object):
    def __init__(self, user_id, starting_system, *a, **kw):
        self.id = user_id
        self.fleet = FleetManager()
        self.resources = ResourceManager()
        self.in_userlist = False
        self.join_time = -1
        self.leave_time = -1
        self.total_time = 0
        self.last_payout = 0
        self.starting_system = starting_system

    def join(self, timestamp):
        if self.in_userlist:
            # already in userlist
            return

        self.in_userlist = True
        self.join_time = timestamp
        self.last_payout = timestamp

    def leave(self, timestamp):
        if not self.in_userlist:
            # already removed from userlist
            return

        self.in_userlist = False
        self.leave_time = timestamp

    def update(self, timestamp):
        if not self.in_userlist:
            # at least until there are some other things that affect an
            # offline user.  We may have to split this up into the two
            # parts when that happens.
            return

        # pay out resources
        # XXX consider tracking the last payout time inside the resource
        # instance?
        self.resources.produce_income(timestamp - self.last_payout)
        self.total_time += timestamp - self.last_payout
        self.last_payout = timestamp

    def inspect(self):
        output_str = f"""inspect:
id: {self.id}
{self.fleet}
{self.resources}
in_userlist: {self.in_userlist}
join_time: {self.join_time}
leave_time = {self.leave_time}
total_time = {self.total_time}
last_payout = {self.last_payout}
starting_system = {self.starting_system.name}
"""
        return output_str

    def can_afford(self, ship_or_structure):
        money = ship_or_structure['cost']['money']
        basic = ship_or_structure['cost']['basic_materials']
        advanced = ship_or_structure['cost']['advanced_materials']
        return self.resources.can_afford(money, basic, advanced)

    def spend(self, ship_or_structure):
        money = ship_or_structure['cost']['money']
        basic = ship_or_structure['cost']['basic_materials']
        advanced = ship_or_structure['cost']['advanced_materials']
        return self.resources.spend(money, basic, advanced)

    def has_structure(self, system, structure):
        sources = self.resources.income_sources
        return structure['name'] in sources.get(system.name, {}).keys()

    def construct_starting_structure(self, structure):
        """
        Construct a starting structure in the starting system
        """
        system = self.starting_system
        money = structure['cost']['money']
        basic = structure['cost']['basic_materials']
        advanced = structure['cost']['advanced_materials']
        self.resources.one_time_income(money, basic, advanced)
        self.construct_building(system, structure)

    def construct_building(self, system, structure):
        if not self.can_afford(structure):
            raise ValueError(f"idleiss.User.construct_building: {structure['name']} costs too much for {self.id} to afford")
        if self.has_structure(system, structure):
            raise ValueError(f"idleiss.User.construct_building: {structure['name']} already built for {self.id} in {system.name}")
        # spend resources
        self.spend(structure)
        # update solar system
        system_name = system.name
        structure_name = structure['name']
        money_income = structure['produces']['money']
        basic_income = structure['produces']['basic_materials']
        adv_income = structure['produces']['advanced_materials']
        # update user
        self.resources.add_income_source(system_name, structure_name, basic_income, adv_income, money_income)
        # update system
        system.add_structure(self.id, structure)

    def conquer_new_system(self, system, structure):
        """
        Construct an Infrastructure Control Hub which can be placed in an unclaimed system
        consumes Structure Gantry
        """
        if not structure['sov_structure']:
            raise ValueError(f"idleiss.User.conquer_new_system: {self.id}: {structure['name']} is not a sov_structure")
        if system.owned_by != None:
            raise ValueError(f"idleiss.User.conquer_new_system: {user.id}: {system.name} is not free to be conquered")
        system.owned_by = self.id
        self.construct_citadel(system, structure)
