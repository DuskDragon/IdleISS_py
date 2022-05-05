from unittest import TestCase

from idleiss import resource

class ResourceTestCase(TestCase):
    def test_resource_payment(self):
        resources = resource.ResourceManager()
        resources.basic_materials_income = 1
        resources.advanced_materials_income = 1
        resources.money_income = 1
        resources.produce_income(10)
        self.assertEqual(resources.basic_materials, 10)
        self.assertEqual(resources.advanced_materials, 10)
        self.assertEqual(resources.money, 10)

    def test_resource_source_add(self):
        resources = resource.ResourceManager()
        resources.add_structure("Sol", "Earth", 50, 50, 100)
        self.assertEqual(resources.basic_materials_income, 50)
        self.assertEqual(resources.advanced_materials_income, 50)
        self.assertEqual(resources.money_income, 100)
        self.assertEqual(resources.structures, {"Sol": {"Earth": [50, 50 , 100]}})
        resources.add_structure("Sol", "Moon", 5, 5, 10)
        self.assertEqual(resources.basic_materials_income, 55)
        self.assertEqual(resources.advanced_materials_income, 55)
        self.assertEqual(resources.money_income, 110)
        self.assertEqual(resources.structures, {"Sol": {"Earth": [50, 50 , 100], "Moon": [5, 5, 10]}})

    def test_resource_source_removal(self):
        resources = resource.ResourceManager()
        resources.add_structure("Sol", "Earth", 50, 50, 100)
        resources.remove_structure("Sol", "Earth")
        self.assertEqual(resources.basic_materials_income, 0)
        self.assertEqual(resources.advanced_materials_income, 0)
        self.assertEqual(resources.money_income, 0)
        self.assertEqual(resources.structures, {})

    def test_invalid_source_add(self):
        resources = resource.ResourceManager()
        resources.add_structure("Sol", "Earth", 50, 50, 100)
        with self.assertRaises(resource.Location_Already_Exists) as context:
            resources.add_structure("Sol", "Earth", 100, 100, 100)
        self.assertEqual(str(context.exception), "'Earth@Sol already exists.'")

    def test_invalid_source_removal(self):
        resources = resource.ResourceManager()
        with self.assertRaises(resource.Location_Does_Not_Exist) as context:
            resources.remove_structure("Sol", "Earth")
        self.assertEqual(str(context.exception), "'Earth@Sol does not exist.'")
        resources.add_structure("Sol", "Moon", 5, 5, 10)
        with self.assertRaises(resource.Location_Does_Not_Exist) as context:
            resources.remove_structure("Sol", "Earth")
        self.assertEqual(str(context.exception), "'Earth@Sol does not exist.'")

    def test_negative_income_after_removal(self):
        resources = resource.ResourceManager()
        resources.add_structure("Sol", "Earth", 50, 50, 100)
        resources.basic_materials_income = 0
        resources.advanced_materials_income = 0
        resources.money_income = 0
        with self.assertRaises(ValueError) as context:
            resources.remove_structure("Sol", "Earth")
        self.assertEqual(str(context.exception), "Income is negative after removing income source Earth@Sol: -50 -50 -100")

    def test_update_source_income(self):
        resources = resource.ResourceManager()
        resources.add_structure("Sol1", "P1", 50, 50, 100)
        resources.update_structure("Sol1", "P1", 50, 25, 200)
        self.assertEqual(resources.basic_materials_income, 50)
        self.assertEqual(resources.advanced_materials_income, 25)
        self.assertEqual(resources.money_income, 200)
