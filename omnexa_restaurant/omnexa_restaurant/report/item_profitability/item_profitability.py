import frappe
from frappe import _


def execute(filters=None):
	rows = frappe.db.sql(
		"""
		SELECT
			oi.menu_item,
			COALESCE(SUM(oi.quantity), 0) AS qty_sold,
			COALESCE(SUM(oi.line_amount), 0) AS sales_amount,
			COALESCE(SUM(oi.line_cost), 0) AS cost_amount,
			COALESCE(SUM(oi.line_amount - oi.line_cost), 0) AS profit_amount
		FROM `tabRestaurant Order Item` oi
		INNER JOIN `tabRestaurant Order` o ON o.name = oi.parent
		WHERE o.docstatus = 1
		GROUP BY oi.menu_item
		ORDER BY profit_amount DESC
		""",
		as_dict=True,
	)
	return _columns(), rows


def _columns():
	return [
		{"label": _("Menu Item"), "fieldname": "menu_item", "fieldtype": "Link", "options": "Menu Item", "width": 180},
		{"label": _("Qty Sold"), "fieldname": "qty_sold", "fieldtype": "Float", "width": 90},
		{"label": _("Sales"), "fieldname": "sales_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Cost"), "fieldname": "cost_amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Profit"), "fieldname": "profit_amount", "fieldtype": "Currency", "width": 130},
	]

