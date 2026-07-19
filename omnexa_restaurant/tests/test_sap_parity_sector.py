# Copyright (c) 2026, ErpGenEx
from frappe.tests.utils import FrappeTestCase

from omnexa_core.omnexa_core.vertical_parity import preview_for_vertical


class TestSapParitySector(FrappeTestCase):
	def test_vertical_kpi_preview(self):
		out = preview_for_vertical("restaurant", revenue=1000, cogs=400)
		self.assertEqual(out["vertical"], "restaurant")
		self.assertIn("kpi", out)
		self.assertIn("sap_module", out)
