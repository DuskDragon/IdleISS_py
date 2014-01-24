from math import log

from .user import User


class TimeOutofBounds(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class GameEngine(object):

    def __init__(self):
        self.users = {}

        # The current world_timestamp - only updated whenever the world
        # is updated by calling update_world with the current/latest
        # simulated timestamp.
        self.world_timestamp = 0

    def get_user(self, user_id):
        if user_id not in self.users:
            raise ValueError
        return self.users[user_id]

    def user_logged_in(self, user_id, timestamp):
        if user_id not in self.users:
            # create a user if that user_id is never seen before.
            self.users[user_id] = User(user_id)

    # Honestly I'm not even sure if I want to penalize messages ... hmmm
    #def user_room_message(self, user_id, message, timestamp):
        #however penalties are not yet implemented
    #    if user_id not in self.users:
    #        raise ValueError

    #    self.users[user_id].last_active = timestamp

    def user_logged_out(self, user_id, timestamp):
        user = self.get_user(user_id)
        self.add_event(user.log_out, timestamp=timestamp)

    def update_world(self, timestamp):
        if timestamp == self.world_timestamp:
            return []
        if timestamp < self.world_timestamp:
            # can't go back in time for now.
            raise TimeOutofBounds("already processed this timestamp")

        time_diff = timestamp - self.world_timestamp
        
        result = []

        #### Pay Resources and Update total_idle_time
        for user_id in self.users:
            user = self.get_user(user_id)
            if not user.online:
                # skip offline users.
                continue

            user.update(timestamp)

            #### Random Events
            #### Calculate Battles
            #### Produce Units
            #### Other Events?

        self.world_timestamp = timestamp
        return result
