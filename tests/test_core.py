from unittest import TestCase

from idleiss import core


class CoreTestCase(TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_base_game(self):
        engine = core.GameEngine()
        self.assertTrue(engine)

    def test_no_such_user(self):
        engine = core.GameEngine()

    def test_base_login(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        idleness = engine.get_user_idleness('an_user', timestamp=1010)
        self.assertEqual(idleness, 10)

    def test_user_interaction(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        engine.user_room_message('an_user', 'some_message', timestamp=1006)
        idleness = engine.get_user_idleness('an_user', timestamp=1010)
        self.assertEqual(idleness, 4)
