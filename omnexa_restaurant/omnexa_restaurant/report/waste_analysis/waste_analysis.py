import frappe
from frappe import _


def execute(filters=None):
	rows = frappe.db.sql(
		"""
		SELECT branch, item, reason, COALESCE(SUM(qty), 0) AS total_qty, COALESCE(SUM(cost_impact), 0) AS total_cost_impact
		FROM `tabWaste Log`
		WHERE docstatus < 2
		GROUP BY branch, item, reason
		ORDER BY total_cost_impact DESC
		""",
		as_dict=True,
	)
	return _columns(), rows


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 170},
		{"label": _("Reason"), "fieldname": "reason", "fieldtype": "Data", "width": 140},
		{"label": _("Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
		{"label": _("Cost Impact"), "fieldname": "total_cost_impact", "fieldtype": "Currency", "width": 130},
	]

