from unittest import TestCase

from idleiss.user import User

class UserTestCase(TestCase):

    def setUp(self):
        self.user = User('an_user')
    
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
