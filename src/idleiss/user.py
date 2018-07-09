from .fleet import FleetManager
from .resource import ResourceManager

class User(object):
    def __init__(self, user_id, *a, **kw):
        self.id = user_id
        self.fleet = FleetManager()
        self.resources = ResourceManager()
        self.online = False
        self.online_at = -1
        #self.last_active = -1
        self.offline_at = -1
        self.total_idle_time = 0

        self.last_payout = 0

    def get_current_idle_duration(self, timestamp):
        if not self.online:
            return 0
        return timestamp - self.online_at

    def log_in(self, timestamp):
        if self.online:
            # already logged in
            return

        self.online = True
        self.online_at = timestamp
        self.last_payout = timestamp

    def log_out(self, timestamp):
        if not self.online:
            # already logged out
            return

        self.online = False
        self.offline_at = timestamp

    def update(self, timestamp):
        if not self.online:
            # at least until there are some other things that affect an
            # offline user.  We may have to split this up into the two
            # parts when that happens.
            return

        # pay out resources
        # XXX consider tracking the last payout time inside the resource
        # instance?
        self.resources.pay_resources(timestamp - self.last_payout)
        self.last_payout = timestamp
        # update idle time
        self.total_idle_time += timestamp - self.online_at

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
