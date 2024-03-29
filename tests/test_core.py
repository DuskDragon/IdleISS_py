from unittest import TestCase
from os.path import join, dirname
import json

from idleiss import core
from idleiss.event import HighEnergyScan

path_to_file = lambda fn: join(dirname(__file__), "data", fn)


class CoreTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_base_game(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        self.assertTrue(engine)

    def test_update_world_basic(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        user_list = set(["an_user"])
        engine.update_world(active_list=user_list, timestamp=1000)
        # manually set one of the income rates
        engine.users["an_user"].resources.basic_materials_income = 1
        engine.users["an_user"].resources.advanced_materials_income = 1
        engine.users["an_user"].resources.money_income = 1

        # check that income is paid properly
        engine.update_world(active_list=user_list, timestamp=1007)
        self.assertEqual(engine.users["an_user"].resources.basic_materials, 7)
        self.assertEqual(engine.users["an_user"].resources.advanced_materials, 7)
        self.assertEqual(engine.users["an_user"].resources.money, 7)

        # can't trigger the same events again I guess?
        engine.update_world(active_list=user_list, timestamp=1007)
        self.assertEqual(engine.users["an_user"].resources.basic_materials, 7)
        self.assertEqual(engine.users["an_user"].resources.advanced_materials, 7)
        self.assertEqual(engine.users["an_user"].resources.money, 7)

        engine.update_world(active_list=user_list, timestamp=1008)
        self.assertEqual(engine.users["an_user"].resources.basic_materials, 8)
        self.assertEqual(engine.users["an_user"].resources.advanced_materials, 8)
        self.assertEqual(engine.users["an_user"].resources.money, 8)

    def test_offline_users_do_not_earn_resources(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        user_list = set(["user1", "user2"])
        engine.update_world(active_list=user_list, timestamp=1000)
        engine.users["user1"].resources.basic_materials_income = 1
        engine.users["user2"].resources.basic_materials_income = 1
        user_list = set(["user1"])
        engine.update_world(active_list=user_list, timestamp=1001)

        # now user1 and user2 should both have 1 basic_material
        self.assertEqual(engine.users["user1"].resources.basic_materials, 1)
        self.assertEqual(engine.users["user2"].resources.basic_materials, 1)

        engine.update_world(active_list=user_list, timestamp=1002)
        #now user1 should have 2, while user2 still has only 1
        self.assertEqual(engine.users["user1"].resources.basic_materials, 2)
        self.assertEqual(engine.users["user2"].resources.basic_materials, 1)

    def test_events_skip_time(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        user_list = set(["an_user"])
        engine.update_world(active_list=user_list, timestamp=1000)
        # manually set one of the income rates
        engine.users["an_user"].resources.basic_materials_income = 1
        engine.users["an_user"].resources.advanced_materials_income = 1
        engine.users["an_user"].resources.money_income = 1
        engine.update_world(active_list=user_list, timestamp=2100)

        # check that income was paid properly
        self.assertEqual(engine.users["an_user"].resources.basic_materials, 1100)
        self.assertEqual(engine.users["an_user"].resources.advanced_materials, 1100)
        self.assertEqual(engine.users["an_user"].resources.money, 1100)

    def test_backwards_in_time_failure(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        user_list = set(["an_user"])
        engine.update_world(active_list=user_list, timestamp=1000)
        with self.assertRaises(core.TimeOutofBounds) as context:
            engine.update_world(active_list=user_list, timestamp=999)
        self.assertEqual(str(context.exception), "'already processed this timestamp'")

    def test_event_engine_add(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        user_list = set(["user1"])
        engine.update_world(active_list=user_list, timestamp=1)
        some_event = HighEnergyScan(timestamp=1, user="user1", constellations=[engine.universe.constellations[0].name])
        engine._add_event(some_event)
        self.assertEqual(engine._engine_events[0], some_event)

    def test_inspect_user(self):
        engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        user_list = set(["user1", "user2"])
        engine.update_world(active_list=user_list, timestamp=1)
        # manually setting income sources
        engine.users["user1"].resources.basic_materials_income = 1
        engine.users["user1"].resources.advanced_materials_income = 1
        engine.users["user1"].resources.money_income = 1
        # update for 10 seconds
        engine.update_world(active_list=user_list, timestamp=11)
        # inspect user1 and print all properties
        starting_system_name = engine.users["user1"].starting_system.name
        # formatting of a dict in a string is a mess so here is a bad workaround:
        sources_string = r"{'"+f"{starting_system_name}"+r"': {'Outpost': [1, 0, 1]}}"
        expected_string = f"""inspect:
id: user1
fleet: {{}}
resources: [10, 10, 10]
\tincome: [1, 1, 1]
\tsources: {sources_string}
in_userlist: True
join_time: 1
leave_time: -1
total_time: 10
last_payout: 11
starting_system: {starting_system_name}
last_low_scan: None
last_focus_scan: None
last_high_scan: None
destinations: []"""
        self.assertEqual(expected_string,engine.inspect_user("user1"))

    #TODO
    # def test__prune_destinations

    #TODO
    # def test__high_energy_scan

    #TODO
    # def test_events_occur_in_order(self):
        # def func_a(timestamp):
            # return 'a'
        # def func_b(timestamp):
            # return 'b'
        # def func_c(timestamp):
            # return 'c'
        # def func_d(timestamp):
            # return 'd'
        # engine = core.GameEngine(path_to_file("Small_Universe_Config.json"), path_to_file("Ships_Config.json"), path_to_file("Scan_Config.json"))
        # user_list = set(["user1", "user2"])
        # engine.update_world(active_list=user_list, timestamp=1)
        # engine._add_event(func_a, timestamp=2)
        # engine._add_event(func_b, timestamp=3)
        # engine._add_event(func_c, timestamp=4)
        # engine._add_event(func_d, timestamp=5)
        # expected_val = ['2: a','3: b', '4: c', '5: d']
        # mes_manager = engine.update_world(active_list=user_list, timestamp=5)
        # self.assertEqual(expected_val, mes_manager.broadcasts_with_times)

    def test_loaded_save_files_generate_same_save_files_to_active_engines(self):
        engine1 = core.GameEngine(
            path_to_file("Small_Universe_Config.json"),
            path_to_file("Ships_Config.json"),
            path_to_file("Scan_Config.json")
        )
        user_list = ["user1", "user2"]
        engine1.update_world(user_list, timestamp=1)
        shared_save_json = json.dumps(engine1.generate_savedata())
        shared_save = json.loads(shared_save_json)
        engine2 = core.GameEngine(
            path_to_file("Small_Universe_Config.json"),
            path_to_file("Ships_Config.json"),
            path_to_file("Scan_Config.json"),
            shared_save
        )
        self.assertEqual(engine1.generate_savedata(), engine2.generate_savedata())
        engine1.update_world(user_list, timestamp=51)
        engine2.update_world(user_list, timestamp=51)
        self.assertEqual(engine1.generate_savedata(), engine2.generate_savedata())

    def test_different_timestamps_produce_different_outputs(self):
        engine1 = core.GameEngine(
            path_to_file("Small_Universe_Config.json"),
            path_to_file("Ships_Config.json"),
            path_to_file("Scan_Config.json")
        )
        user_list = ["user1", "user2"]
        engine1.update_world(user_list, timestamp=1)
        shared_save_json = json.dumps(engine1.generate_savedata())
        shared_save = json.loads(shared_save_json)
        engine2 = core.GameEngine(
            path_to_file("Small_Universe_Config.json"),
            path_to_file("Ships_Config.json"),
            path_to_file("Scan_Config.json"),
            shared_save
        )
        self.assertEqual(engine1.generate_savedata(), engine2.generate_savedata())
        engine1.update_world(user_list, timestamp=51)
        engine2.update_world(user_list, timestamp=50)
        self.assertNotEqual(engine1.generate_savedata(), engine2.generate_savedata())

    def test_a_large_number_of_users_can_save(self):
        engine = core.GameEngine(
            path_to_file("Small_Universe_Config.json"),
            path_to_file("Ships_Config.json"),
            path_to_file("Scan_Config.json")
        )
        user_list = [f'user{x}' for x in range(50)]
        engine.update_world(user_list, timestamp=1)
        shared_save_json = json.dumps(engine.generate_savedata())
        shared_save = json.loads(shared_save_json)