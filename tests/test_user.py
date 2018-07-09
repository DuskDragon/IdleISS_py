from unittest import TestCase

from idleiss.user import User

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
        self.user = User("an_user", LibraryStub())

    def test_log_in(self):
        user = self.user
        user.log_in(100)
        self.assertTrue(user.online)
        self.assertEqual(user.online_at, 100)

        # already logged in, no effect on online_at
        user.log_in(200)
        self.assertNotEqual(user.online_at, 200)

        # XXX game states will have to clean itself up from unclean
        # shutdowns - i.e. it could store the last time it was running as
        # the logoff time for users, log everyone out, then log them back
        # on as part of its startup routine.

    def test_log_out(self):
        user = self.user
        user.log_out(100)
        # default state is not logged in, so can't log out.
        self.assertNotEqual(user.offline_at, 100)

        user.log_in(100)
        user.log_out(200)
        self.assertFalse(user.online)
        self.assertEqual(user.offline_at, 200)

    def test_idle_duration(self):
        user = self.user
        user.log_in(100)
        self.assertEqual(user.get_current_idle_duration(105), 5)

        # user never idle when logged out
        user.log_out(200)
        self.assertEqual(user.get_current_idle_duration(205), 0)

    def test_update(self):
        user = self.user
        # manually set one of the income rates
        user.resources.money_income = 1
        user.update(50)
        # offline users won't get updated.
        self.assertEqual(user.resources.money, 0)

        user.log_in(100)
        user.update(107)
        self.assertEqual(user.resources.money, 7)
