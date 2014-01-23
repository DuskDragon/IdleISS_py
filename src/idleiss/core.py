class GameEngine(object):

    def __init__(self):
        self.users = {}

    def user_logged_in(self, user, timestamp=None):
        if user not in self.users:
            self.users[user] = {}
            self.users[user]['last_idle'] = timestamp

    def user_room_message(self, user, message, timestamp=None):
        if user not in self.users:
            return

        self.users[user]['last_idle'] = timestamp

    def user_logged_out(self, user, timestamp=None):
        pass

    def get_user_idleness(self, user, timestamp=None):
        if user not in self.users:
            raise ValueError

        return timestamp - self.users[user]['last_idle']
