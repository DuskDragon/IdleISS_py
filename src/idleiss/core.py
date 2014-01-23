class GameEngine(object):

    def __init__(self):
        self.users = {}

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
