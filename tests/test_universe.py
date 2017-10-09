from unittest import TestCase

from idleiss.universe import Universe

class UserTestCase(TestCase):

    def setUp(self):
        self.uni = Universe(42, 5100, 340, 68, 3)

    def test_generate_constellation(self):
        pass




#from idleiss.universe import Universe
#uni = Universe(42, 5100, 340, 68, 3)
#uni.generate_constellation(15)
#uni.generate_wolfram_alpha_output(uni.sys)
#Graph 5->14, 9->8, 6->10, 3->4, 15->12, 4->3, 7->10, 13->3, 8->3, 5->7, 10->7, 5->3, 3->5, 2->3, 9->2, 13->9, 15->9, 7->5, 8->1, 11->9, 2->13, 12->11, 10->6, 14->11, 14->5, 3->2, 2->6, 15->10, 13->5, 10->4, 1->8, 6->2, 11->13, 1->14, 5->12, 12->1, 8->9, 5->13, 3->11, 12->5, 1->12, 5->9, 11->14, 1->15, 3->13, 4->12, 4->10, 2->9, 11->12, 12->4, 13->11, 10->15, 7->2, 9->15, 9->5, 9->11, 6->7, 7->6, 3->8, 11->3, 2->11, 11->2, 9->13, 2->7, 13->2, 14->1, 6->3, 12->15, 3->6, 15->1
