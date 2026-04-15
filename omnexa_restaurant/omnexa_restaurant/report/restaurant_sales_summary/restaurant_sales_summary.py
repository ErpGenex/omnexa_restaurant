import frappe
from frappe import _


def execute(filters=None):
	rows = frappe.db.sql(
		"""
		SELECT branch, order_type, status, COUNT(name) AS orders_count, COALESCE(SUM(total_amount),0) AS total_sales
		FROM `tabRestaurant Order`
		WHERE docstatus = 1
		GROUP BY branch, order_type, status
		ORDER BY total_sales DESC
		""",
		as_dict=True,
	)
	return _columns(), rows


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Order Type"), "fieldname": "order_type", "fieldtype": "Data", "width": 110},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Orders"), "fieldname": "orders_count", "fieldtype": "Int", "width": 90},
		{"label": _("Total Sales"), "fieldname": "total_sales", "fieldtype": "Currency", "width": 140},
	]

