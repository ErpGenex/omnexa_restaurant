# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
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
			DATE_FORMAT(o.creation, '%%Y-%%m') AS period,
			COUNT(*) AS orders_count,
			COALESCE(SUM(o.total_amount), 0) AS total_sales,
			COALESCE(SUM(o.cost_amount), 0) AS total_cost,
			COALESCE(SUM(o.total_amount - o.cost_amount), 0) AS gross_profit
		FROM `tabRestaurant Order` o
		WHERE {' AND '.join(conditions)}
		GROUP BY o.branch, DATE_FORMAT(o.creation, '%%Y-%%m')
		ORDER BY period DESC, total_sales DESC
		""",
		filters,
		as_dict=True,
	)

	for row in data:
		row["total_sales"] = flt(row.total_sales)
		row["total_cost"] = flt(row.total_cost)
		row["gross_profit"] = flt(row.gross_profit)
		s = row["total_sales"]
		row["gross_margin_pct"] = flt(100.0 * row["gross_profit"] / s, 2) if s else 0.0

	return _columns(), data


def _columns():
	return [
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		{"label": _("Period (YYYY-MM)"), "fieldname": "period", "fieldtype": "Data", "width": 110},
		{"label": _("Orders"), "fieldname": "orders_count", "fieldtype": "Int", "width": 90},
		{"label": _("Revenue"), "fieldname": "total_sales", "fieldtype": "Currency", "width": 130},
		{"label": _("Cost of sales"), "fieldname": "total_cost", "fieldtype": "Currency", "width": 130},
		{"label": _("Gross profit"), "fieldname": "gross_profit", "fieldtype": "Currency", "width": 130},
		{"label": _("Gross margin %"), "fieldname": "gross_margin_pct", "fieldtype": "Float", "width": 110},
	]
