# Copyright (c) 2026, Omnexa and contributors
# License: See license.txt

from __future__ import annotations

import frappe
from frappe.utils import add_to_date, now_datetime


def process_kitchen_ticket_sla_breaches():
	"""Escalate open kitchen tickets that exceeded station SLA."""
	now = now_datetime()
	rows = frappe.get_all(
		"Kitchen Ticket",
		filters={"docstatus": ["<", 2], "status": ["in", ["Queued", "In Progress"]]},
		fields=["name", "creation", "station", "status"],
		limit_page_length=500,
	)
	for row in rows:
		sla_minutes = frappe.db.get_value("Kitchen Station", row.station, "target_prep_minutes") or 15
		breach_at = add_to_date(row.creation, minutes=sla_minutes)
		if breach_at >= now:
			continue
		doc = frappe.get_doc("Kitchen Ticket", row.name)
		if doc.status != "Delayed":
			doc.status = "Delayed"
			doc.save(ignore_permissions=True)
