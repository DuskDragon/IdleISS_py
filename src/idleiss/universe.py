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

    def flood(self, node):
        if(node.flooded):
            return
        node.flooded = True
        for x in node.connections:
            self.flood(x)

    def floodfill(self, node_list):
        self.flood(node_list[0])
        for x in node_list:
            if x.flooded == False: # found an unconnected node, eject
                for y in node_list: #reset flood state
                    y.flooded = False
                return False
        # no unconnected nodes were found
        for x in node_list: #reset flood state
            x.flooded = False
        return True

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

    def generate_constellation(self, system_count):
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

        # floodfill
        #PDB
        self.sys = system_list
        #ENDPDB
        return system_list[0].floodfill(system_list)
