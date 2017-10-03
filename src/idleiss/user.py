from .fleet import FleetManager
from .resource import ResourceManager
import random

def generate_alphanumeric():
    valid_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return random.choice(valid_characters)

def generate_system_name():
    #example D-PNP9, 6VDT-H, OWXT-5, 16P-PX, CCP-US
    #always uppercase letters
    #5 characters with a dash in the middle somewhere
    dash_position = random.randint(1,4)
    letters = ''.join((generate_alphanumeric() for x in range(5)))
    return letters[0:dash_position] + '-' + letters[dash_position::]

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

    def init_conquer_new_system():
        """
        Construct an Infrastructure Control Hub which can be placed in an unclaimed system
        consumes Structure Gantry
        """
        pass

    def construct_citadel():
        """
        Citadels will function as money generators and basic material generators,
        consumes Structure Gantry
        """
        pass

    def construct_drilling_platform():
        """
        Drilling Platforms will function as basic and advanced material generators,
        consumes Structure Gantry
        """
        pass

    def construct_engineering_complex():
        """
        Engineering Complexes will produce ships and structures,
        consumes Structure Gantry
        """
        pass
