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
        self.assertRaises(ValueError,
            engine.get_user_idleness, 'an_user', timestamp=1010)

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

    def test_events_basic(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        engine.user_room_message('an_user', 'some_message', timestamp=1006)
        events = engine.get_events(timestamp=1007)
        self.assertEqual(events, {
            'an_user': {
                'new_level': 1,
            }
        })
        self.assertEqual(engine.users['an_user']['level'], 1)

        # can't trigger the same events again I guess?
        events = engine.get_events(timestamp=1007)
        self.assertEqual(events, {})

        events = engine.get_events(timestamp=1008)
        self.assertEqual(events, {
            'an_user': {
                'new_level': 2,
            }
        })
        self.assertEqual(engine.users['an_user']['level'], 2)

    def test_events_skip_time(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        engine.user_room_message('an_user', 'some_message', timestamp=2000)
        events = engine.get_events(timestamp=2100)
        self.assertEqual(events, {
            'an_user': {
                'new_level': 7,
            }
        })
        self.assertEqual(engine.users['an_user']['level'], 7)

    def test_events_user_spoke(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        events = engine.get_events(timestamp=1050)
        self.assertEqual(events, {
            'an_user': {
                'new_level': 6,
            }
        })
        engine.user_room_message('an_user', 'some_message', timestamp=1051)
        events = engine.get_events(timestamp=1053)
        # would not trigger the lower level events again
        self.assertEqual(events, {})

        # user level should not decrement either.
        self.assertEqual(engine.users['an_user']['level'], 6)
