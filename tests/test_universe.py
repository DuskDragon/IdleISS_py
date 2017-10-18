from unittest import TestCase
import networkx as nx
import json

from idleiss.universe import Universe

class UserTestCase(TestCase):

    def setUp(self):
        pass

    def test_load_universe_config(self):
        with open("config/Universe_Config.json") as fd:
            raw_data = json.load(fd)

    def test_generate_constellation_raises_error(self):
        uni = Universe(42, 5100, 340, 68, 1.35)
        with self.assertRaises(ValueError):
            constellation = uni.generate_constellation(0)
        with self.assertRaises(ValueError):
            constellation = uni.generate_constellation(1)

    def test_generate_constellation_2_systems(self):
        uni = Universe(42, 5100, 340, 68, 0)
        constellation = uni.generate_constellation(2)
        #uni.generate_networkx(uni.sys)
        graph = uni.generate_networkx(constellation)
        self.assertEqual(graph.number_of_nodes(), 2)
        self.assertEqual(nx.is_connected(graph), True)
        self.assertIs(constellation[0].connections[0], constellation[1])
        self.assertIs(constellation[1].connections[0], constellation[0])

    def test_generate_constellation_15_systems_connected(self):
        uni = Universe(42, 5100, 340, 68, 1.35)
        for x in range(5):
            constellation = uni.generate_constellation(15)
            #uni.generate_networkx(uni.sys)
            graph = uni.generate_networkx(constellation)
            self.assertEqual(graph.number_of_nodes(), 15)
            self.assertEqual(nx.is_connected(graph), True)

#import json
#with open("config/Universe_Config.json") as fd:
#    raw_data = json.load(fd)
#
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


#Highsec:
#Suroken
#Halaima
#Ikao
#Kamio
#Sankkasen
#Santola
#Tintoh
#Waira
#Ealur
#Fahruni
#Ishisomo - Uoyonen, Akkilen - Vattuolen
#Charak (only systems in the const not charak itself)
#Shemah
#Telang
#Zorrabed
#Akhwa
#Halibai
#Kothe
#Sonama
#Suner
#Turba

#Lowsec:
#Annancale
#Harroule
#Vey
