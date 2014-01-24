from unittest import TestCase

from idleiss import resource

class ResourceTestCase(TestCase):
     def test_resource_payment(self):
        resources = resource.ResourceManager()
        resources.basic_materials_income = 1
        resources.advanced_materials_income = 1
        resources.money_income = 1
        resources.pay_resources(10)
        self.assertEqual(resources.basic_materials, 10)
        self.assertEqual(resources.advanced_materials, 10)
        self.assertEqual(resources.money, 10)
