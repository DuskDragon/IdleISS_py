from unittest import TestCase

from idleiss.universe import Universe

class UserTestCase(TestCase):

    def setUp(self):
        self.uni = Universe(42, 5100, 340, 68, 3)

    def test_generate_constellation(self):
        pass




#from idleiss.universe import Universe
#uni = Universe(42, 5100, 340, 68, 1.74)
#uni.generate_constellation(15)
#uni.generate_wolfram_alpha_output(uni.sys)
#uni.generate_networkx(uni.sys)
#uni.G

#from idleiss.universe import Universe; uni = Universe(42, 5100, 340, 68, 1.74); uni.generate_constellation(15); uni.generate_networkx(uni.sys)

#uni.generate_constellation(15); uni.generate_networkx(uni.sys)
