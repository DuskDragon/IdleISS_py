from math import log
from user import User

class TimeOutofBounds(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class GameEngine(object):

    def __init__(self):
        self.users = {}
        
        #last_event_called_timestamp is updated 
        #by get_events each time it is called
        self.last_event_called_timestamp = 0

    def user_logged_in(self, user_id, timestamp):
        if user_id not in self.users:
            self.users[user_id] = User(user_id)
        
        self.users[user_id].online_at = timestamp
        #self.users[user_id].last_active = timestamp

    # Honestly I'm not even sure if I want to penalize messages ... hmmm
    #def user_room_message(self, user_id, message, timestamp):
        #however penalties are not yet implemented
    #    if user_id not in self.users:
    #        raise ValueError

    #    self.users[user_id].last_active = timestamp

    def user_logged_out(self, user_id, timestamp):
        if user_id not in self.users:
            raise ValueError

        self.users[user_id].online = False
        self.users[user_id].offline_at = timestamp
        
        # pay resources and update total idle time since last get_events or online
        if self.last_event_called_timestamp < self.users[user_id].online_at:
            self.users[user_id].resources.pay_resources(timestamp - self.users[user_id].online_at)
            self.users[user_id].total_idle_time += timestamp - self.users[user_id].online_at 
        else: 
            self.users[user_id].resources.pay_resources(timestamp - self.last_event_called_timestamp)
            self.users[user_id].total_idle_time += timestamp - self.last_event_called_timestamp 

    def get_user_current_idle_duration(self, user_id, timestamp):
        if user_id not in self.users:
            raise ValueError

        return timestamp - self.users[user_id].online_at

    def get_events(self, timestamp):
        if timestamp == self.last_event_called_timestamp:
            return []
        if timestamp < self.last_event_called_timestamp:
            # can't go back in time for now.
            raise TimeOutofBounds("get_events: Timestamps are going backwards in time")

        time_diff = timestamp - self.last_event_called_timestamp
        
        result = []

        #### Pay Resources and Update total_idle_time
        for user_id in self.users:
            user = self.users[user_id]
            #user is online, but logged in since the last get_events
            if user.online and self.last_event_called_timestamp < user.online_at:
                user.resources.pay_resources(timestamp - user.online_at)
                user.total_idle_time += timestamp - user.online_at
            elif user.online:
                user.resources.pay_resources(time_diff)
                user.total_idle_time += time_diff
        #### Random Events
        for user_id in self.users:
            pass
        #### Calculate Battles
        for user_id in self.users:
            pass
        #### Produce Units
        for user_id in self.users:
            pass
        #### Other Events?
        for user_id in self.users:
            pass


        
        self.last_event_called_timestamp = timestamp
        return result
