import frappe
from frappe import _


def execute(filters=None):
	rows = frappe.db.sql(
		"""
		SELECT
			mi.kitchen_station,
			COUNT(DISTINCT oi.parent) AS orders_count,
			COALESCE(SUM(oi.quantity), 0) AS total_qty
		FROM `tabRestaurant Order Item` oi
		INNER JOIN `tabRestaurant Order` o ON o.name = oi.parent
		INNER JOIN `tabMenu Item` mi ON mi.name = oi.menu_item
		WHERE o.docstatus = 1
		GROUP BY mi.kitchen_station
		ORDER BY orders_count DESC
		""",
		as_dict=True,
	)
	return _columns(), rows


def _columns():
	return [
		{"label": _("Kitchen Station"), "fieldname": "kitchen_station", "fieldtype": "Link", "options": "Kitchen Station", "width": 180},
		{"label": _("Orders"), "fieldname": "orders_count", "fieldtype": "Int", "width": 110},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 110},
	]

