from .fleet import FleetManager
from .resource import ResourceManager

class User(object):
    def __init__(self, user_id, *a, **kw):
        self.id = user_id
        self.fleet = FleetManager()
        self.resources = ResourceManager()
        self.in_userlist = False
        self.join_time = -1
        self.leave_time = -1
        self.total_time = 0
        self.last_payout = 0

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
        self.resources.pay_resources(timestamp - self.last_payout)
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
last_payout = {self.last_payout}"""
        return output_str

    def init_conquer_new_system(self):
        """
        Construct an Infrastructure Control Hub which can be placed in an unclaimed system
        consumes Structure Gantry
        """
        pass

    def construct_citadel(self):
        """
        Citadels will function as money generators and basic material generators,
        consumes Structure Gantry
        """
        pass

    def construct_drilling_platform(self):
        """
        Drilling Platforms will function as basic and advanced material generators,
        consumes Structure Gantry
        """
        pass

    def construct_engineering_complex(self):
        """
        Engineering Complexes will produce ships and structures,
        consumes Structure Gantry
        """
        pass
