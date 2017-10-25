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
        self.assertTrue(nx.is_connected(graph))

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


###########NetworkX##############
#import matplotlib.pyplot as plt
#import networkx as nx
#from idleiss.universe import Universe
#uni = Universe('config/Universe_Config.json')
#systems = uni.generate_networkx(uni.systems)
#print("Total System Nodes: "+str(systems.number_of_nodes())+", Edges: "+str(systems.number_of_edges()))
#regions = uni.generate_networkx(uni.regions)
#print("Total Region Nodes: "+str(regions.number_of_nodes())+", Edges: "+str(regions.number_of_edges()))
#constellations = uni.generate_networkx(uni.constellations)
#print("Total Constellation Nodes: "+str(constellations.number_of_nodes())+", Edges: "+str(constellations.number_of_edges()))
#the_forge = [r for r in uni.regions if r.name == "The Forge"][0]
#forge_systems = []
#for const in the_forge.constellations:
#    for system in const.systems:
#        forge_systems.append(system)
#
#forge_graph = uni.generate_networkx(forge_systems)
#print(f'The Forge Systems: {forge_graph.number_of_nodes()}, Edges: {forge_graph.number_of_edges()}')
#
#
#nx.draw_networkx(forge_graph, pos=nx.spring_layout(forge_graph), with_labels=True)
#plt.show()
#
#
#nx.draw_networkx(regions, pos=nx.spring_layout(regions), with_labels=True)
#plt.show()


###########Graph-Tool############
#from idleiss.universe import Universe
#uni = Universe('config/Universe_Config.json')
#graph = uni.generate_graph_tool(uni.systems)
#from graph_tool.draw import graph_draw
#graph_draw(graph, vertex_text=graph.vertex_properties["name"], vertex_font_size=10, edge_pen_width=1.2, output_size=(5000,5000), output="node_list.png")
#graph_draw(graph, vertex_size=5, edge_pen_width=1.2, output_size=(4000, 4000), output="node_list_no_names.png")
