from unittest import TestCase
import networkx as nx
import json

from idleiss.universe import Universe

class UserTestCase(TestCase):

    def setUp(self):
        pass

    def test_load_universe_config(self):
        uni = Universe('config/Universe_Config.json')
        graph = uni.generate_networkx(uni.systems)
        self.assertEqual(graph.number_of_nodes(), 5100)

    # def test_generate_constellation_raises_error(self):
        # uni = Universe()
        # uni.rand.seed(42)
        # uni.connectedness = 1.35
        # with self.assertRaises(ValueError):
            # constellation = uni.generate_constellation(0)
        # with self.assertRaises(ValueError):
            # constellation = uni.generate_constellation(1)

    # def test_generate_constellation_2_systems(self):
        # uni = Universe()
        # uni.rand.seed(42)
        # uni.connectedness = 1.35
        # constellation = uni.generate_constellation(2)
        # #uni.generate_networkx(uni.sys)
        # graph = uni.generate_networkx(constellation)
        # self.assertEqual(graph.number_of_nodes(), 2)
        # self.assertEqual(nx.is_connected(graph), True)
        # self.assertIs(constellation[0].connections[0], constellation[1])
        # self.assertIs(constellation[1].connections[0], constellation[0])

    # def test_generate_constellation_15_systems_connected(self):
        # uni = Universe()
        # uni.rand.seed(42)
        # uni.connectedness = 1.35
        # for x in range(5):
            # constellation = uni.generate_constellation(15)
            # #uni.generate_networkx(uni.sys)
            # graph = uni.generate_networkx(constellation)
            # self.assertEqual(graph.number_of_nodes(), 15)
            # self.assertEqual(nx.is_connected(graph), True)

#for x in raw_data["Universe_Structure"]:
#    if raw_data["Universe_Structure"][x]["Security"] == "High":
#        print(x)

#from idleiss.universe import Universe
#uni = Universe(42, 5100, 340, 68, 1.35)
#uni.generate_constellation(15)
#uni.generate_wolfram_alpha_output(uni.sys)
#uni.generate_networkx(uni.sys)

#from idleiss.universe import Universe; uni = Universe(42, 5100, 340, 68, 1.74); uni.generate_constellation(15); uni.generate_networkx(uni.sys)

#uni.generate_constellation(15); uni.generate_networkx(uni.sys)


###########Graph-Tool############
#from idleiss.universe import Universe
#uni = Universe('config/Universe_Config.json')
#graph = uni.generate_graph_tool(uni.systems)
#from graph_tool.draw import graph_draw
#graph_draw(graph, vertex_text=graph.vertex_properties["name"], vertex_font_size=6, edge_pen_width=1.2, output_size=(4000,4000), output="node_list.png")
