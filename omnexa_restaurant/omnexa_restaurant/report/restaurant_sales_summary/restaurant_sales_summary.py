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
		{"label": _("Order Type"), "fieldname": "order_type", "fieldtype": "Data", "width": 110},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Orders"), "fieldname": "orders_count", "fieldtype": "Int", "width": 90},
		{"label": _("Total Sales"), "fieldname": "total_sales", "fieldtype": "Currency", "width": 140},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Restaurant Order", date_field="creation", company=True, branch=True)
	conditions = ["docstatus = 1"] + conditions
	rows = frappe.db.sql(
		f"""
		SELECT
			branch, order_type, status, COUNT(name) AS orders_count, COALESCE(SUM(total_amount),0) AS total_sales
		FROM `tabRestaurant Order`
		WHERE {' AND '.join(conditions)}
		GROUP BY branch, order_type, status
		ORDER BY total_sales DESC
		""",
		params,
		as_dict=True,
	)
	return columns, rows
