from frappe.tests.utils import FrappeTestCase

from omnexa_restaurant import hooks


class TestRestaurantSmoke(FrappeTestCase):
	def test_hooks_are_present(self):
		self.assertEqual(hooks.app_name, "omnexa_restaurant")
		self.assertIn("omnexa_accounting", hooks.required_apps)

