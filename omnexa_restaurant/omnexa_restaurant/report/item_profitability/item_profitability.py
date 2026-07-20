# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	columns = [
		{"label": _("Menu Item"), "fieldname": "menu_item", "fieldtype": "Link", "options": "Menu Item", "width": 180
	},
		{"label": _("Qty Sold"), "fieldname": "qty_sold", "fieldtype": "Float", "width": 90
	},
		{"label": _("Sales"), "fieldname": "sales_amount", "fieldtype": "Currency", "width": 130
	},
		{"label": _("Cost"), "fieldname": "cost_amount", "fieldtype": "Currency", "width": 130
	},
		{"label": _("Profit"), "fieldname": "profit_amount", "fieldtype": "Currency", "width": 130
	},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Restaurant Order Item", date_field="creation", company=True, branch=True)
	conditions = ["docstatus = 1"] + conditions
	rows = frappe.db.sql(
		f"""
		SELECT
			oi.menu_item,
			COALESCE(SUM(oi.quantity), 0) AS qty_sold,
			COALESCE(SUM(oi.line_amount), 0) AS sales_amount,
			COALESCE(SUM(oi.line_cost), 0) AS cost_amount,
			COALESCE(SUM(oi.line_amount - oi.line_cost), 0) AS profit_amount
		FROM `tabRestaurant Order Item`
		WHERE {' AND '.join(conditions)}
		GROUP BY oi.menu_item
		ORDER BY profit_amount DESC
		""",
		params,
		as_dict=True,
	)
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart