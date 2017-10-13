import random

def generate_alphanumeric(random_state):
    valid_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return random_state.choice(valid_characters)

def generate_system_name(random_state):
    #example D-PNP9, 6VDT-H, OWXT-5, 16P-PX, CCP-US
    #always uppercase letters
    #5 characters with a dash in the middle somewhere
    dash_position = random_state.randint(1,4)
    letters = ''.join((generate_alphanumeric(random_state) for x in range(5)))
    return letters[0:dash_position] + '-' + letters[dash_position::]

def flood(node):
    if(node.flooded):
        return
    node.flooded = True
    for x in node.connections:
        flood(x)

def floodfill(node_list):
    flood(node_list[0])
    for x in node_list:
        if x.flooded == False: # found an unconnected node, eject
            return False
    # no unconnected nodes were found
    return True

def drain(node_list):
    for x in node_list: #reset flood state
        x.flooded = False

class SolarSystem(object):
    def __init__(self, system_id, random_state, universe):
        unvalidated_name = generate_system_name(random_state)
        while(universe.system_name_exists(unvalidated_name)):
            unvalidated_name = generate_system_name(random_state)
        self.name = unvalidated_name
        universe.register_system_name(self.name)
        self.id = system_id
        self.connections = []
        self.flooded = False

    def __str__(self):
        connections_str = ""
        for x in self.connections:
            connections_str += " " + str(x.id)
        return "idleiss.universe.SolarSystem: " + str(self.id) + " Connections: " + connections_str

    def connection_exists(self, system):
        return system in self.connections

    def add_connection(self, system):
        if self.connection_exists(system):
            return False # may want to change this return type (means already connected)
        self.connections.append(system)
        if system.connection_exists(self):
            raise ValueError("1-way System Connection: "+system.name+" to "+self.name)
        system.connections.append(self)
        return True # connection added

class Universe(object):
    def __init__(self, seed, systems, constellations, regions, connectedness):
        """
        generates a universe with #systems, #constellations and #regions
        using connectedness as a rough guide to how linked nodes are within a collection
        """
        self.rand = random
        self.rand.seed(seed)
        self.system_count_target = systems
        self.constellation_count_target = constellations
        self.region_count_target = regions
        self.connectedness = connectedness
        self.system_names = []
        self.current_unused_system_id = 0

    def register_system_name(self, name):
        if self.system_name_exists(name):
            raise ValueError("Universe generation: system name exists: "+name)
        else:
            self.system_names.append(name)

    def system_name_exists(self, name):
        return name in self.system_names

    def generate_wolfram_alpha_output(self, node_list):
        connection_list = []
        for x in node_list:
            for y in x.connections:
                if x.id > y.id:
                    connection_list.append(str(x.id+1) + "->" + str(y.id+1) + ", ")
                else: # y > x:
                    connection_list.append(str(y.id+1) + "->" + str(x.id+1) + ", ")
        pruned_list = set(connection_list)
        output_str = "Graph "
        for x in pruned_list:
            output_str += str(x)
        return output_str[:-2]

    def generate_networkx(self, node_list):
        """
        Debugging function which uses NetworkX (python mathematics tool)
        NetworkX is a fully python implementation so don't use HUGE graphs
        it's 225x slower than graph-tool (implemented as a C++ library with python wrapper)
        """
        import networkx as nx
        G = nx.Graph()
        connection_list = []
        orphan_list = []
        for x in node_list:
            if len(x.connections) == 0:
                orphan_list.append(x.id)
            for y in x.connections:
                if x.id > y.id:
                    connection_list.append((x.id,y.id,))
                else: # y > x:
                    connection_list.append((y.id,x.id,))
        pruned_list = set(connection_list)
        # add collected nodes
        G.add_edges_from(pruned_list)
        G.add_nodes_from(orphan_list)
        ## TODO: clean up when not needed
        ## debug info
        #print("Nodes: "+str(G.number_of_nodes())+", Edges: "+str(G.number_of_edges()))
        #import matplotlib.pyplot as plt
        #plt.subplot(111)
        #nx.draw_networkx(G, with_labels=True)
        #plt.show()
        return G

    def generate_constellation(self, system_count):
        if system_count < 2:
            raise ValueError("must have at least two systems for a constellation")
        system_list = []
        for x in range(system_count):
            system_list.append(SolarSystem(self.current_unused_system_id, self.rand, self))
            self.current_unused_system_id += 1
        # now we have a list of systems which each have an id and a name
        # we just need to randomly add connections
        # at first we won't care if they are already connected

        # develop 'connectedness * system_count' connections
        for x in range(int(self.connectedness*system_count)):
            s1, s2 = self.rand.sample(system_list, 2)
            s1.add_connection(s2)

        #def stitch_nodes(self, node_list):
        # floodfill
        if len(system_list[0].connections) == 0: #floodfill will start on orphan, avoid this
            system_list[0].add_connection(self.rand.choice(system_list[1:]))
        while not floodfill(system_list):
            #floodfill failed, find failed nodes:
            valid_nodes = []
            orphan_nodes = []
            disjoint_nodes = []
            for x in system_list:
                if len(x.connections) == 0:
                    orphan_nodes.append(x)
                elif x.flooded:
                    valid_nodes.append(x)
                else: # not flooded, not orphan, must be disjoint
                    disjoint_nodes.append(x)
            #first pin disjoint graphs to valid nodes
            if len(disjoint_nodes) > 0:
                disjoint_nodes[0].add_connection(self.rand.choice(valid_nodes))
                drain(system_list)
                continue #go around again
            #next pin all orphans, there are only ophans remaining
            for x in range(len(orphan_nodes)): #include already processed orphans
                orphan_nodes[x].add_connection(self.rand.choice((valid_nodes + orphan_nodes[:x])))
            drain(system_list)
        #end of floodfill
        drain(system_list)
        return system_list
