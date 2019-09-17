from unittest import TestCase

from idleiss.user import User

class SolarSystemStub(object):
    def __init__(self):
        self.name = "SolarStub"

class LibraryStub(object):
    def __init__(self):
        self.size_data = [
            "one"
        ]
        self.hullclasses = [
            "generic"
        ]
        self.ship_data = {
            "ship1": {
                "hullclass": "generic",
                "shield": 10,
                "armor": 10,
                "hull": 100,
                "weapons": [
                    {
                        "weapon_name": "gun",
                        "weapon_size": "one",
                        "firepower": 50,
                        "priority_targets": [
                            ["ship1",],
                        ],
                    },
                ],
                "sensor_strength": 1,
                "size": "one",
            }
        }

    def ship_shield(self, name):
        return self.ship_data[name]["shield"]
    def ship_armor(self, name):
        return self.ship_data[name]["armor"]
    def ship_hull(self, name):
        return self.ship_data[name]["hull"]
    def ship_firepower(self, name):
        return self.ship_data[name]["firepower"]

class UserTestCase(TestCase):

    def setUp(self):
        self.user = User("an_user", SolarSystemStub())

    def test_log_in(self):
        user = self.user
        user.join(100)
        self.assertTrue(user.in_userlist)
        self.assertEqual(user.join_time, 100)

        # already logged in, no effect on online_at
        user.join(200)
        self.assertNotEqual(user.join_time, 200)

        # XXX game states will have to clean itself up from unclean
        # shutdowns - i.e. it could store the last time it was running as
        # the logoff time for users, log everyone out, then log them back
        # on as part of its startup routine.

    def test_log_out(self):
        user = self.user
        user.leave(100)
        # default state is not logged in, so can't log out.
        self.assertNotEqual(user.leave_time, 100)

        user.join(100)
        user.leave(200)
        self.assertFalse(user.in_userlist)
        self.assertEqual(user.leave_time, 200)

    def test_update(self):
        user = self.user
        # manually set one of the income rates
        user.resources.money_income = 1
        user.update(50)
        # offline users won't get updated.
        self.assertEqual(user.resources.money, 0)

        user.join(100)
        user.update(107)
        self.assertEqual(user.resources.money, 7)
