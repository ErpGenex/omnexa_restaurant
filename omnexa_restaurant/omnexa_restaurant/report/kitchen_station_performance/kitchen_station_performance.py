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
		{"label": _("Kitchen Station"), "fieldname": "kitchen_station", "fieldtype": "Link", "options": "Kitchen Station", "width": 180},
		{"label": _("Orders"), "fieldname": "orders_count", "fieldtype": "Int", "width": 110},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 110},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Restaurant Order Item", date_field="creation", company=True, branch=True)
	conditions = ["docstatus = 1"] + conditions
	rows = frappe.db.sql(
		f"""
		SELECT
			mi.kitchen_station,
			COUNT(DISTINCT oi.parent) AS orders_count,
			COALESCE(SUM(oi.quantity), 0) AS total_qty
		FROM `tabRestaurant Order Item`
		WHERE {' AND '.join(conditions)}
		GROUP BY mi.kitchen_station
		ORDER BY orders_count DESC
		""",
		params,
		as_dict=True,
	)
	return columns, rows
