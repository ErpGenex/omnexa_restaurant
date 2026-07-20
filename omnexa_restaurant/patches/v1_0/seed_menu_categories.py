# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Seed default Arabic menu categories for restaurant POS."""

from __future__ import annotations

import frappe

DEFAULT_CATEGORIES = (
	("Appetizers", "المقبلات", 1),
	("Main Dishes", "الأطباق الرئيسية", 2),
	("Side Dishes", "الأطباق الجانبية", 3),
	("Drinks", "المشروبات", 4),
	("Desserts", "الحلويات", 5),
)


def execute():
	company = frappe.defaults.get_global_default("company") or frappe.db.get_single_value(
		"Global Defaults", "default_company"
	)
	if not company:
		return
	branches = frappe.get_all("Branch", filters={"company": company
	}, pluck="name") or [None]
	for branch in branches:
		for en_name, ar_name, sort_order in DEFAULT_CATEGORIES:
			if frappe.db.exists("Menu Category", en_name):
				continue
			doc = frappe.get_doc(
				{
					"doctype": "Menu Category",
					"category_name": en_name,
					"name_ar": ar_name,
					"sort_order": sort_order,
					"company": company,
					"branch": branch,
					"is_active": 1
	}
			)
			doc.insert(ignore_permissions=True)
	frappe.db.commit()
