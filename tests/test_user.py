from unittest import TestCase

from idleiss.user import User

import json

class SolarSystemStub(object):
    def __init__(self, name="SolarStub", id=0):
        self.name = name
        self.id = id
        self.structures = {}

    def add_structure(self, user_id, structure):
        if structure['name'] in self.structures.get(user_id, []):
            raise ValueError(f"SolarSystemStub.add_structure: {structure['name']} already built for {user_id} in {self.name}")
        temp = self.structures.get(user_id, [])
        temp.append(structure['name'])
        self.structures[user_id] = temp

# class StructureStub(object):
    # def __init__(self, name="structure",
                       # money=1,
                       # basic_materials=1,
                       # advanced_materials=1
    # ):
        # self.name = name
        # self.money = money
        # self.basic_materials = basic_materials
        # self.advanced_materials = advanced_materials

class LibraryStub(object):
    def __init__(self):
        self.size_data = [
            "one"
        ]
        self.hullclasses = [
            "generic"
        ]
        self.ship_data = {
            "ship1": {
                "hullclass": "generic",
                "shield": 10,
                "armor": 10,
                "hull": 100,
                "weapons": [
                    {
                        "weapon_name": "gun",
                        "weapon_size": "one",
                        "firepower": 50,
                        "priority_targets": [
                            ["ship1",],
                        ],
                    },
                ],
                "sensor_strength": 1,
                "size": "one",
            }
        }
        self.strucutre_data = {
            "test_starting_structure": {
                "name": "test_starting_structure",
                # "shield": 1,
                # "armor": 1,
                # "hull": 1,
                # "sensor_strength": 1,
                # "weapons": [],
                # "hullclass": "structure",
                # "size": "structure",
                # "structure_tier": 0,
                # "reinforce_cycles": 1,
                # "security": "high",
                # "shipyard": [],
                "produces": {
                    "money": 1,
                    "basic_materials": 1,
                    "advanced_materials": 1
                },
                # "sov_structure": true,
                "cost": {
                    "money": 5,
                    "basic_materials": 5,
                    "advanced_materials": 5
                }
            }
        }

    def ship_shield(self, name):
        return self.ship_data[name]["shield"]
    def ship_armor(self, name):
        return self.ship_data[name]["armor"]
    def ship_hull(self, name):
        return self.ship_data[name]["hull"]
    def ship_firepower(self, name):
        return self.ship_data[name]["firepower"]

class UserTestCase(TestCase):

    def setUp(self):
        self.user = User("an_user", SolarSystemStub())

    def test_log_in(self):
        user = self.user
        user.join(100)
        self.assertTrue(user.in_userlist)
        self.assertEqual(user.join_time, 100)

        # already logged in, no effect on online_at
        user.join(200)
        self.assertNotEqual(user.join_time, 200)

        # XXX game states will have to clean itself up from unclean
        # shutdowns - i.e. it could store the last time it was running as
        # the logoff time for users, log everyone out, then log them back
        # on as part of its startup routine.

    def test_log_out(self):
        user = self.user
        user.leave(100)
        # default state is not logged in, so can't log out.
        self.assertNotEqual(user.leave_time, 100)

        user.join(100)
        user.leave(200)
        self.assertFalse(user.in_userlist)
        self.assertEqual(user.leave_time, 200)

    def test_update(self):
        user = self.user
        # manually set one of the income rates
        user.resources.money_income = 1
        user.update(50)
        # offline users won't get updated.
        self.assertEqual(user.resources.money, 0)

        user.join(100)
        user.update(107)
        self.assertEqual(user.resources.money, 7)

    def test_can_afford(self):
        user = self.user
        ship_stub = {"cost": {"money": 5, "basic_materials": 5, "advanced_materials": 5}}
        # user.resources.basic_materials = 0
        # user.resources.advanced_materials = 0
        # user.resources.money = 0
        self.assertFalse(user.can_afford(ship_stub))
        user.resources.basic_materials = 5
        self.assertFalse(user.can_afford(ship_stub))
        user.resources.advanced_materials = 5
        self.assertFalse(user.can_afford(ship_stub))
        user.resources.money = 5
        self.assertTrue(user.can_afford(ship_stub))

    def test_can_load_users_accurately(self):
        user1 = User("user1", SolarSystemStub())
        user1.join(0)
        self.library = LibraryStub()
        structure = self.library.strucutre_data['test_starting_structure']
        money = structure['cost']['money']
        basic_materials = structure['cost']['basic_materials']
        advanced_materials = structure['cost']['advanced_materials']
        user1.resources.one_time_income(money, basic_materials, advanced_materials)
        self.assertTrue(user1.can_afford(structure))
        user1.construct_building(SolarSystemStub(), structure)
        savedict = user1.generate_savedata()
        savejson = json.dumps(savedict)
        user1.update(50)
        structure_basic_materials_produced = structure['produces']['basic_materials']
        self.assertEqual(structure_basic_materials_produced*50, user1.resources.basic_materials)

        #core.py must replace all solar system ids with the actual solar
        #system class instance before it is loaded by the User constructor
        #we are stubbing out everything else so the test must perform this action
        loaded_dict = json.loads(savejson)
        loaded_dict['starting_system'] = SolarSystemStub()

        user_copy = User(0, 0, loaded_dict) #TODO? clean this up: User's ugly constructor
        user_copy.update(50)
        self.assertEqual(structure_basic_materials_produced*50, user_copy.resources.basic_materials)
        savedict = user1.generate_savedata()
        savejson = json.dumps(savedict)
        save_copy_dict = user_copy.generate_savedata()
        save_copy_json = json.dumps(savedict)
        #both copies should behave the exact same and produce the same save data
        self.assertEqual(savejson, save_copy_json)
