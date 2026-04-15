# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

import frappe

from omnexa_core.omnexa_core.branch_access import enforce_branch_access, get_allowed_branches
from omnexa_core.omnexa_core.user_context import apply_company_branch_defaults


def enforce_branch_access_for_doc(doc, method=None):
	enforce_branch_access(doc)


def populate_company_branch_from_user_context(doc, method=None):
	apply_company_branch_defaults(doc)


def _get_query_for_table(table: str, user=None):
	user = user or frappe.session.user
	allowed = get_allowed_branches(user)
	if allowed is None:
		return ""
	if not allowed:
		return "1=0"
	quoted = ", ".join([frappe.db.escape(v) for v in allowed])
	return f"(`tab{table}`.branch in ({quoted}) or `tab{table}`.branch is null or `tab{table}`.branch = '')"


def restaurant_floor_query_conditions(user=None):
	return _get_query_for_table("Restaurant Floor", user)


def restaurant_table_query_conditions(user=None):
	return _get_query_for_table("Restaurant Table", user)


def kitchen_station_query_conditions(user=None):
	return _get_query_for_table("Kitchen Station", user)


def kitchen_printer_query_conditions(user=None):
	return _get_query_for_table("Kitchen Printer", user)


def menu_item_query_conditions(user=None):
	return _get_query_for_table("Menu Item", user)


def restaurant_recipe_query_conditions(user=None):
	return _get_query_for_table("Restaurant Recipe", user)


def restaurant_order_query_conditions(user=None):
	return _get_query_for_table("Restaurant Order", user)


def delivery_zone_query_conditions(user=None):
	return _get_query_for_table("Delivery Zone", user)


def waste_log_query_conditions(user=None):
	return _get_query_for_table("Waste Log", user)


def delivery_driver_query_conditions(user=None):
	return _get_query_for_table("Delivery Driver", user)


def kitchen_ticket_query_conditions(user=None):
	return _get_query_for_table("Kitchen Ticket", user)


def kitchen_print_template_query_conditions(user=None):
	return _get_query_for_table("Kitchen Print Template", user)


def kitchen_print_job_query_conditions(user=None):
	return _get_query_for_table("Kitchen Print Job", user)

