from .fleet import FleetManager
from .resource import ResourceManager
#from .scan import SiteInstance

class User(object):
    def __init__(self, user_id, starting_system, savedata=None):
        if savedata == None:
            self.id = user_id
            self.fleet = FleetManager()
            self.resources = ResourceManager()
            self.in_userlist = False
            self.join_time = -1
            self.leave_time = -1
            self.total_time = 0
            self.last_payout = 0
            self.starting_system = starting_system
            self.last_low_scan = None
            self.last_focus_scan = None
            self.last_high_scan = None
            self.destinations = []
            return
        #TODO add validation
        self.id = savedata['id']
        self.fleet = FleetManager(savedata['fleet_save'])
        self.resources = ResourceManager(savedata['resources_save'])
        self.in_userlist = savedata['in_userlist']
        self.join_time = savedata['join_time']
        self.leave_time = savedata['leave_time']
        self.total_time = savedata['total_time']
        self.last_payout = savedata['last_payout']
        self.starting_system = savedata['starting_system']
        self.last_low_scan = savedata['last_low_scan']
        self.last_focus_scan = savedata['last_focus_scan']
        self.last_high_scan = savedata['last_high_scan']
        self.destinations = savedata['destinations']

    def generate_savedata(self):
        save = {
            'id': self.id,
            'fleet_save' : self.fleet.ships,
            'resources_save': self.resources.generate_savedata(),
            'in_userlist': self.in_userlist,
            'join_time': self.join_time,
            'leave_time': self.leave_time,
            'total_time': self.total_time,
            'last_payout': self.last_payout,
            'starting_system': self.starting_system.id,
            'last_low_scan': self.last_low_scan,
            'last_focus_scan': self.last_focus_scan,
            'last_high_scan': self.last_high_scan,
            'destinations': self.destinations,
        }
        return save

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
leave_time: {self.leave_time}
total_time: {self.total_time}
last_payout: {self.last_payout}
starting_system: {self.starting_system.name}
last_low_scan: {self.last_low_scan}
last_focus_scan: {self.last_focus_scan}
last_high_scan: {self.last_high_scan}
destinations: {self.destinations}"""
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
        sources = self.resources.structures
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
        self.resources.add_structure(system_name, structure_name, basic_income, adv_income, money_income)
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
            raise ValueError(f"idleiss.User.conquer_new_system: {self.id}: {system.name} is not free to be conquered")
        system.owned_by = self.id
        self.construct_citadel(system, structure)
