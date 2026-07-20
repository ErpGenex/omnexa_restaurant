# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns
from frappe.utils import flt
from omnexa_core.omnexa_core.branch_access import get_allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	conditions = ["o.docstatus = 1", "o.company = %(company)s"]
	if filters.get("branch"):
		conditions.append("o.branch = %(branch)s")
	if filters.get("from_date"):
		conditions.append("DATE(o.creation) >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("DATE(o.creation) <= %(to_date)s")

	allowed = get_allowed_branches(company=filters.company)
	if allowed is not None:
		if not allowed:
			return _columns(), []
		filters.allowed_branches = tuple(allowed)
		conditions.append("o.branch in %(allowed_branches)s")

	data = frappe.db.sql(
		f"""
		SELECT
			o.branch,
			DATE(o.creation) AS sales_date,
			COUNT(*) AS orders_count,
			COALESCE(SUM(o.total_amount), 0) AS total_sales
		FROM `tabRestaurant Order` o
		WHERE {' AND '.join(conditions)}
		GROUP BY o.branch, DATE(o.creation)
		ORDER BY sales_date DESC, o.branch
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["total_sales"] = flt(row.total_sales)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140
	},
		{"label": _("Date"), "fieldname": "sales_date", "fieldtype": "Date", "width": 120
	},
		{"label": _("Orders"), "fieldname": "orders_count", "fieldtype": "Int", "width": 90
	},
		{"label": _("Revenue"), "fieldname": "total_sales", "fieldtype": "Currency", "width": 140
	},
	]
