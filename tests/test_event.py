from unittest import TestCase

from idleiss.event import Event


class EventTestCase(TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_event(self):
        def a_function(a=1, b=2):
            return (b, a)
        event = Event(a_function, a=2, b=3)
        result = event()
        self.assertEqual(result, (3, 2))
