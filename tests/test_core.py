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
            engine.get_user_current_idle_duration, 'an_user', timestamp=1010)
        self.assertRaises(ValueError,
            engine.user_logged_out, 'an_user', timestamp=1010)

    def test_base_login(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        idleness = engine.get_user_current_idle_duration('an_user', timestamp=1010)
        self.assertEqual(idleness, 10)

    # def test_user_interaction(self):
        # engine = core.GameEngine()
        # engine.user_logged_in('an_user', timestamp=1000)
        # engine.user_room_message('an_user', 'some_message', timestamp=1006)
        # idleness = engine.get_user_current_idleduration('an_user', timestamp=1010)
        # self.assertEqual(idleness, 4)

    def test_events_basic(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        engine.users['an_user'].resources.basic_materials_income = 1
        engine.users['an_user'].resources.advanced_materials_income = 1
        engine.users['an_user'].resources.money_income = 1
        events = engine.get_events(timestamp=1007)
        self.assertEqual(events, [])
        self.assertEqual(engine.users['an_user'].resources.basic_materials,7)
        self.assertEqual(engine.users['an_user'].resources.advanced_materials, 7)
        self.assertEqual(engine.users['an_user'].resources.money, 7)

        # can't trigger the same events again I guess?
        events = engine.get_events(timestamp=1007)
        self.assertEqual(events, [])
        self.assertEqual(engine.users['an_user'].resources.basic_materials, 7)
        self.assertEqual(engine.users['an_user'].resources.advanced_materials, 7)
        self.assertEqual(engine.users['an_user'].resources.money, 7)

        events = engine.get_events(timestamp=1008)
        self.assertEqual(events, [])

        self.assertEqual(engine.users['an_user'].resources.basic_materials, 8)
        self.assertEqual(engine.users['an_user'].resources.advanced_materials, 8)
        self.assertEqual(engine.users['an_user'].resources.money, 8)

    def test_events_skip_time(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        engine.users['an_user'].resources.basic_materials_income = 1
        engine.users['an_user'].resources.advanced_materials_income = 1
        engine.users['an_user'].resources.money_income = 1
        events = engine.get_events(timestamp=2100)
        self.assertEqual(events, [])
        self.assertEqual(engine.users['an_user'].resources.basic_materials, 1100)
        self.assertEqual(engine.users['an_user'].resources.advanced_materials, 1100)
        self.assertEqual(engine.users['an_user'].resources.money, 1100)

    # def test_events_user_spoke(self):
        # engine = core.GameEngine()
        # engine.user_logged_in('an_user', timestamp=1000)
        # events = engine.get_events(timestamp=1050)
        # self.assertEqual(events, {
            # 'an_user': {
                # 'new_level': 6,
            # }
        # })
        # engine.user_room_message('an_user', 'some_message', timestamp=1051)
        # events = engine.get_events(timestamp=1053)
        ##would not trigger the lower level events again
        # self.assertEqual(events, {})

        ##user level should not decrement either.
        # self.assertEqual(engine.users['an_user']['level'], 6)
        
    def test_backwards_in_time_failure(self):
        engine = core.GameEngine()
        engine.user_logged_in('an_user', timestamp=1000)
        engine.get_events(timestamp=1050)
        self.assertRaises(core.TimeOutofBounds, engine.get_events, timestamp=999)
            
    def test_log_in_between_ticks(self):
        engine = core.GameEngine()
        engine.get_events(timestamp=100)
        engine.user_logged_in('an_user', timestamp=150)
        engine.users['an_user'].resources.basic_materials_income = 1
        engine.get_events(timestamp=200)
        self.assertEqual(engine.users['an_user'].resources.basic_materials, 50)
    
    def test_log_in_log_out_between_ticks(self):
        engine = core.GameEngine()
        events = engine.get_events(timestamp=100)
        engine.user_logged_in('an_user', timestamp=150)
        engine.users['an_user'].resources.basic_materials_income = 1
        engine.user_logged_out('an_user', timestamp=170)
        events = engine.get_events(timestamp=200)
        self.assertEqual(engine.users['an_user'].resources.basic_materials, 20)
        
    def test_log_in_backwards_in_time(self):
        engine = core.GameEngine()
        events = engine.get_events(timestamp=100)
        self.assertRaises(core.TimeOutofBounds, engine.user_logged_in, 'an_user', timestamp=50)
    
    def test_log_out_backwards_in_time(self):
        engine = core.GameEngine()
        events = engine.get_events(timestamp=100)
        engine.user_logged_in('an_user', timestamp=101)
        self.assertRaises(core.TimeOutofBounds, engine.user_logged_out, 'an_user', timestamp=50)
        
        
