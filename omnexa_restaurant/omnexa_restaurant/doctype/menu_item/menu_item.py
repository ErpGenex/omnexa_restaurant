# Copyright (c) 2026, Omnexa and contributors
# License: MIT

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class MenuItem(Document):
	def validate(self):
		if self.item_type == "Bundle" and not self.bundle_items:
			frappe.throw(_("Bundle items are required for bundle menu items."))
		if self.item_type == "Raw Material" and flt(self.default_price):
			frappe.throw(_("Raw materials should not have a selling price on the menu."))
		if self.menu_category and not self.category:
			cat_name = frappe.db.get_value("Menu Category", self.menu_category, "category_name")
			if cat_name:
				self.category = cat_name
		if self.category and not self.menu_category:
			match = frappe.db.get_value(
				"Menu Category",
				{"category_name": self.category, "company": self.company, "branch": self.branch
	},
				"name",
			)
			if match:
				self.menu_category = match

	def on_update(self):
		if self.item_type in ("Product", "Service", "Bundle") and not self.erp_item:
			self._ensure_erp_item_link()

	def _ensure_erp_item_link(self):
		from omnexa_restaurant.pos_invoicing import ensure_erp_item_for_menu_item

		item_code = ensure_erp_item_for_menu_item(self)
		if item_code and item_code != self.erp_item:
			frappe.db.set_value("Menu Item", self.name, "erp_item", item_code, update_modified=False)
