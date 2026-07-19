from __future__ import annotations

import frappe


def ensure_restaurant_kpi_cards():
	card_defs = [
		("Active Orders", "omnexa_restaurant.api.kpi_active_orders"),
		("Occupied Tables", "omnexa_restaurant.api.kpi_occupied_tables"),
		("Revenue Today", "omnexa_restaurant.api.kpi_revenue_today"),
		("Waste Cost MTD", "omnexa_restaurant.api.kpi_waste_cost_mtd"),
	]
	card_names = []
	for label, method in card_defs:
		card_name = frappe.db.get_value("Number Card", {"label": label, "method": method}, "name")
		if not card_name:
			card = frappe.new_doc("Number Card")
			card.label = label
			card.type = "Custom"
			card.method = method
			card.module = "Omnexa Restaurant"
			card.is_public = 1
			card.show_percentage_stats = 0
			card.insert(ignore_permissions=True)
			card_name = card.name
		card_names.append(card_name)

	workspace = frappe.get_doc("Workspace", "Restaurant")
	workspace.number_cards = []
	for name in card_names:
		workspace.append("number_cards", {"number_card_name": name})
	workspace.save(ignore_permissions=True)
	frappe.db.commit()
	return {"workspace": workspace.name, "number_cards": card_names}

