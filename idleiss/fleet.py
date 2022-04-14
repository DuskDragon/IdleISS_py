
class FleetManager(object):

    def __init__(self, ships=None):
        # ships are a dict for now.
        # keys are ship_ids (which seems to be category of ships for now)
        # and value is how many there are.
        if ships is None:
            ships = {}
        self.ships = ships

    def __str__(self):
        return f"fleet: {self.ships}"

    def add_ship(self, ship_id, amount):
        if amount > 0:
            self.ships[ship_id] = self.ships.get(ship_id, 0) + amount
        else:
            raise ValueError("Amount of ships added cannot be zero or less")

    def contains_ship(self, ship_id, number=1):
        if number < 1:
            raise ValueError("Amount of ships cannot be less than 1")
        if ship_id in self.ships.keys():
            if self.ships[ship_id] >= number:
                return True
            else:
                return False
        else:
            return False

    # def contains_ship(self, ship_id, number):
        # if number == 0:
            # return True
        # if ship_id in self.ships.keys():
            # if self.ships[ship_id] >= number:
                # return True
            # else:
                # return False
        # else:
            # return False

    def remove_ship(self, ship_id, num):
        if num < 1:
            raise ValueError("Cannot remove negative or zero ships")

        if not (self.contains_ship(ship_id, num)):
            return False
        else:
            self.ships[ship_id] -= num
            if self.ships[ship_id] == 0:
                self.ships.pop(ship_id)
            return True
