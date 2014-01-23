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
