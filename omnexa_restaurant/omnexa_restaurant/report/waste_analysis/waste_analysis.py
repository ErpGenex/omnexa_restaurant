# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	columns = [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 170},
		{"label": _("Reason"), "fieldname": "reason", "fieldtype": "Data", "width": 140},
		{"label": _("Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
		{"label": _("Cost Impact"), "fieldname": "total_cost_impact", "fieldtype": "Currency", "width": 130},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Waste Log", date_field="creation", company=True, branch=True)
	rows = frappe.db.sql(
		f"""
		SELECT
			branch, item, reason, COALESCE(SUM(qty), 0) AS total_qty, COALESCE(SUM(cost_impact), 0) AS total_cost_impact
		FROM `tabWaste Log`
		WHERE {' AND '.join(conditions)}
		GROUP BY branch, item, reason
		ORDER BY total_cost_impact DESC
		""",
		params,
		as_dict=True,
	)
	return columns, rows
