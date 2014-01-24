from fleet import FleetManager
from resource import ResourceManager

class User(object):
    def __init__(self, user_id):
        self.id = user_id
        self.fleet = FleetManager()
        self.resources = ResourceManager()
        self.online = True
        self.online_at = -1
        #self.last_active = -1
        self.offline_at = -1
        self.total_idle_time = 0
        
