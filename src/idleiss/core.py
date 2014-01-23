from math import log


class GameEngine(object):

    def __init__(self):
        self.users = {}
        self.last_event_timestamp = 0

    def user_logged_in(self, user_id, timestamp):
        if user_id not in self.users:
            self.users[user_id] = {}
            self.users[user_id]['last_idle'] = timestamp

    def user_room_message(self, user_id, message, timestamp):
        if user_id not in self.users:
            return

        self.users[user_id]['last_idle'] = timestamp

    def user_logged_out(self, user_id, timestamp):
        pass

    def get_user_idleness(self, user_id, timestamp):
        if user_id not in self.users:
            raise ValueError

        return timestamp - self.users[user_id]['last_idle']

    def get_events(self, timestamp):
        if timestamp < self.last_event_timestamp:
            # can't go back in time for now.
            return

        self.last_event_timestamp = timestamp

        result = {}

        for user_id in self.users:
            user = self.users[user_id]
            idle_time = self.get_user_idleness(user_id, timestamp)
            # probably have to split this to a dedicated method later.
            user_level = int(log(idle_time, 2)) + 1

            if user_level > user.get('level', 0):
                # should probably create an event object later?
                user['level'] = user_level
                result[user_id] = {
                    'new_level': user_level
                }

        return result
