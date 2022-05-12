from unittest import TestCase

import idleiss.event as Events


class EventTestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_event(self):
        x = Events.HighEnergyScan(timestamp=1, user="user1", constellations=[])
        y = Events.HighEnergyScanAnnouncement(timestamp=0, user="user1", constellations=[])
        self.assertTrue(x>y)
        self.assertTrue(x!=y)
        self.assertTrue(y<x)
