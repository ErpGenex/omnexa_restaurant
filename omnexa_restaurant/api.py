from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, today


@frappe.whitelist()
def assign_delivery_driver(order_name: str, driver: str, eta_mins: int | str = 30):
	order = frappe.get_doc("Restaurant Order", order_name)
	if order.order_type != "Delivery":
		frappe.throw(_("Driver assignment is allowed for Delivery orders only."))
	order.delivery_driver = driver
	order.delivery_status = "Assigned"
	order.eta_mins = cint(eta_mins)
	order.save(ignore_permissions=True)
	driver_doc = frappe.get_doc("Delivery Driver", driver)
	driver_doc.status = "On Delivery"
	driver_doc.save(ignore_permissions=True)
	return {"order": order.name, "delivery_driver": order.delivery_driver, "delivery_status": order.delivery_status}


@frappe.whitelist()
def toggle_hold_order(order_name: str):
	order = frappe.get_doc("Restaurant Order", order_name)
	order.hold_order = 0 if cint(order.hold_order) else 1
	if order.hold_order and order.status == "In Progress":
		order.status = "Draft"
	order.save(ignore_permissions=True)
	return {"order": order.name, "hold_order": order.hold_order, "status": order.status}


@frappe.whitelist()
def generate_kitchen_tickets(order_name: str):
	order = frappe.get_doc("Restaurant Order", order_name)
	station_items: dict[str, list[dict]] = {}
	for row in order.items:
		station = frappe.db.get_value("Menu Item", row.menu_item, "kitchen_station") or "Unassigned"
		station_items.setdefault(station, [])
		station_items[station].append(
			{
				"menu_item": row.menu_item,
				"quantity": row.quantity,
				"modifiers": row.modifiers,
				"notes": row.notes,
			}
		)

	tickets = []
	for station, items in station_items.items():
		printer = frappe.db.get_value("Kitchen Station", station, "printer_assigned") if station != "Unassigned" else None
		ticket = frappe.new_doc("Kitchen Ticket")
		ticket.restaurant_order = order.name
		ticket.kitchen_station = station if station != "Unassigned" else None
		ticket.kitchen_printer = printer
		ticket.ticket_status = "Pending"
		ticket.total_items = sum([flt(i.get("quantity")) for i in items])
		ticket.ticket_payload = json.dumps(
			{
				"order_number": order.name,
				"order_type": order.order_type,
				"table": order.table,
				"items": items,
			}
		)
		ticket.company = order.company
		ticket.branch = order.branch
		ticket.insert(ignore_permissions=True)
		tickets.append(ticket.name)
	return {"order": order.name, "tickets": tickets}


@frappe.whitelist()
def kpi_active_orders():
	value = frappe.db.count("Restaurant Order", {"status": ["in", ["Draft", "In Progress"]]})
	return {"value": cint(value), "fieldtype": "Int", "route": ["List", "Restaurant Order"]}


@frappe.whitelist()
def kpi_occupied_tables():
	value = frappe.db.count("Restaurant Table", {"status": "Occupied"})
	return {"value": cint(value), "fieldtype": "Int", "route": ["List", "Restaurant Table"]}


@frappe.whitelist()
def kpi_revenue_today():
	value = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(total_amount), 0)
		FROM `tabRestaurant Order`
		WHERE docstatus = 1 AND DATE(creation) = %s
		""",
		(getdate(today()),),
	)[0][0]
	return {"value": flt(value), "fieldtype": "Currency", "route": ["List", "Restaurant Order"]}


@frappe.whitelist()
def kpi_waste_cost_mtd():
	value = frappe.db.sql(
		"""
		SELECT COALESCE(SUM(cost_impact), 0)
		FROM `tabWaste Log`
		WHERE MONTH(posting_date) = MONTH(%s) AND YEAR(posting_date) = YEAR(%s)
		""",
		(getdate(today()), getdate(today())),
	)[0][0]
	return {"value": flt(value), "fieldtype": "Currency", "route": ["List", "Waste Log"]}


def _get_editable_order(order_name: str):
	order = frappe.get_doc("Restaurant Order", order_name)
	if order.docstatus != 0:
		frappe.throw(_("Order must be in draft state for this operation."))
	return order


def _copy_order_header(source_order, target_order):
	target_order.order_type = source_order.order_type
	target_order.table = source_order.table
	target_order.customer_profile = source_order.customer_profile
	target_order.delivery_zone = source_order.delivery_zone
	target_order.delivery_driver = source_order.delivery_driver
	target_order.delivery_status = source_order.delivery_status
	target_order.eta_mins = source_order.eta_mins
	target_order.company = source_order.company
	target_order.branch = source_order.branch
	target_order.status = source_order.status


@frappe.whitelist()
def transfer_order(order_name: str, new_table: str):
	order = _get_editable_order(order_name)
	order.table = new_table
	order.save(ignore_permissions=True)
	return {"order": order.name, "table": order.table}


@frappe.whitelist()
def split_bill(order_name: str, item_row_names_json: str | None = None):
	order = _get_editable_order(order_name)
	item_row_names = set(frappe.parse_json(item_row_names_json) or [])
	if not item_row_names:
		frappe.throw(_("Select at least one item row to split."))

	new_order = frappe.new_doc("Restaurant Order")
	_copy_order_header(order, new_order)

	remaining_items = []
	for row in order.items:
		row_payload = {
			"menu_item": row.menu_item,
			"quantity": row.quantity,
			"price": row.price,
			"cost": row.cost,
			"modifiers": row.modifiers,
			"notes": row.notes,
		}
		if row.name in item_row_names:
			new_order.append("items", row_payload)
		else:
			remaining_items.append(row_payload)

	if not new_order.items:
		frappe.throw(_("No matching item rows found for split operation."))
	if not remaining_items:
		frappe.throw(_("Cannot split all items. Keep at least one item in original order."))

	order.items = []
	for row_payload in remaining_items:
		order.append("items", row_payload)
	order.save(ignore_permissions=True)
	new_order.insert(ignore_permissions=True)

	return {"source_order": order.name, "new_order": new_order.name}


@frappe.whitelist()
def merge_tables(primary_order_name: str, secondary_order_name: str):
	primary_order = _get_editable_order(primary_order_name)
	secondary_order = _get_editable_order(secondary_order_name)
	if primary_order.name == secondary_order.name:
		frappe.throw(_("Primary and secondary order cannot be the same."))
	if primary_order.table != secondary_order.table:
		frappe.throw(_("Both orders must belong to the same table to merge."))

	for row in secondary_order.items:
		primary_order.append(
			"items",
			{
				"menu_item": row.menu_item,
				"quantity": row.quantity,
				"price": row.price,
				"cost": row.cost,
				"modifiers": row.modifiers,
				"notes": row.notes,
			},
		)
	primary_order.save(ignore_permissions=True)
	secondary_order.status = "Closed"
	secondary_order.items = []
	secondary_order.save(ignore_permissions=True)
	return {"primary_order": primary_order.name, "merged_order": secondary_order.name}


@frappe.whitelist()
def update_kitchen_ticket_status(ticket_name: str, status: str):
	valid_status = {"Pending", "Preparing", "Ready", "Printed"}
	if status not in valid_status:
		frappe.throw(_("Invalid status for kitchen ticket."))
	ticket = frappe.get_doc("Kitchen Ticket", ticket_name)
	ticket.ticket_status = status
	ticket.save(ignore_permissions=True)
	frappe.publish_realtime(
		"restaurant_kds_update",
		{"ticket": ticket.name, "status": ticket.ticket_status, "order": ticket.restaurant_order},
	)
	return {"ticket": ticket.name, "status": ticket.ticket_status}


@frappe.whitelist()
def get_open_pos_orders():
	return frappe.get_all(
		"Restaurant Order",
		filters={"docstatus": 0, "status": ["in", ["Draft", "In Progress"]]},
		fields=["name", "table", "order_type", "status", "total_amount", "customer_profile"],
		order_by="modified desc",
		limit_page_length=200,
	)


@frappe.whitelist()
def get_pos_catalog():
	items = frappe.get_all(
		"Menu Item",
		filters={"is_active": 1},
		fields=["name", "item_code", "item_name", "category", "default_price"],
		order_by="category asc, item_name asc",
		limit_page_length=1000,
	)
	category_map: dict[str, list[dict]] = {}
	for row in items:
		category = row.category or "General"
		category_map.setdefault(category, [])
		category_map[category].append(row)
	return {"categories": sorted(category_map.keys()), "items_by_category": category_map}


@frappe.whitelist()
def create_pos_order(order_type: str = "Dine-in", table: str | None = None, customer_profile: str | None = None):
	order = frappe.new_doc("Restaurant Order")
	order.order_type = order_type
	order.table = table
	order.customer_profile = customer_profile
	order.status = "Draft"
	order.insert(ignore_permissions=True)
	return {"order_name": order.name}


@frappe.whitelist()
def add_item_to_order(order_name: str, menu_item: str, qty: float | int = 1):
	order = _get_editable_order(order_name)
	qty = flt(qty or 1)
	if qty <= 0:
		frappe.throw(_("Quantity must be greater than zero."))

	price = frappe.db.get_value("Menu Item", menu_item, "default_price") or 0
	existing = None
	for row in order.items:
		if row.menu_item == menu_item and not (row.modifiers or row.notes):
			existing = row
			break
	if existing:
		existing.quantity = flt(existing.quantity) + qty
		existing.price = price
	else:
		order.append("items", {"menu_item": menu_item, "quantity": qty, "price": price, "cost": 0})
	order.status = "In Progress" if order.status == "Draft" else order.status
	order.save(ignore_permissions=True)
	return {"order": order.name, "items_count": len(order.items), "total_amount": order.total_amount}


@frappe.whitelist()
def get_kitchen_tickets(station: str | None = None):
	filters = {"docstatus": ["<", 2], "ticket_status": ["in", ["Pending", "Preparing", "Ready"]]}
	if station:
		filters["kitchen_station"] = station
	return frappe.get_all(
		"Kitchen Ticket",
		filters=filters,
		fields=["name", "restaurant_order", "kitchen_station", "ticket_status", "total_items", "ticket_payload", "modified"],
		order_by="modified asc",
		limit_page_length=200,
	)


@frappe.whitelist()
def get_table_map(floor: str | None = None):
	filters = {"is_active": 1}
	if floor:
		filters["name"] = floor
	floors = frappe.get_all("Restaurant Floor", filters=filters, fields=["name", "floor_name"], order_by="floor_name asc")
	tables = frappe.get_all(
		"Restaurant Table",
		fields=["name", "table_number", "floor", "capacity", "status"],
		order_by="floor asc, table_number asc",
		limit_page_length=1000,
	)
	table_map: dict[str, list[dict]] = {}
	for row in tables:
		table_map.setdefault(row.floor, [])
		table_map[row.floor].append(row)
	return {"floors": floors, "tables_by_floor": table_map}


@frappe.whitelist()
def get_order_items(order_name: str):
	order = frappe.get_doc("Restaurant Order", order_name)
	return [{"row_name": r.name, "menu_item": r.menu_item, "quantity": r.quantity, "line_amount": r.line_amount} for r in order.items]


@frappe.whitelist()
def split_bill_by_item(order_name: str, row_name: str):
	return split_bill(order_name, frappe.as_json([row_name]))


@frappe.whitelist()
def split_bill_by_quantity(order_name: str, row_name: str, quantity: float | int):
	order = _get_editable_order(order_name)
	qty = flt(quantity)
	if qty <= 0:
		frappe.throw(_("Quantity must be greater than zero."))

	target_row = None
	for row in order.items:
		if row.name == row_name:
			target_row = row
			break
	if not target_row:
		frappe.throw(_("Selected order row was not found."))
	if qty >= flt(target_row.quantity):
		frappe.throw(_("Split quantity must be less than existing row quantity."))

	new_order = frappe.new_doc("Restaurant Order")
	_copy_order_header(order, new_order)
	new_order.append(
		"items",
		{
			"menu_item": target_row.menu_item,
			"quantity": qty,
			"price": target_row.price,
			"cost": target_row.cost,
			"modifiers": target_row.modifiers,
			"notes": target_row.notes,
		},
	)
	target_row.quantity = flt(target_row.quantity) - qty
	order.save(ignore_permissions=True)
	new_order.insert(ignore_permissions=True)
	return {"source_order": order.name, "new_order": new_order.name, "split_quantity": qty}


@frappe.whitelist()
def get_kot_print_preview(ticket_name: str):
	ticket = frappe.get_doc("Kitchen Ticket", ticket_name)
	payload = frappe.parse_json(ticket.ticket_payload or "{}")
	items = payload.get("items") or []
	items_text = "\n".join([f"- {i.get('menu_item')} x {i.get('quantity')}" for i in items]) or "-"

	template_text = frappe.db.get_value(
		"Kitchen Print Template",
		{"kitchen_station": ticket.kitchen_station, "company": ticket.company, "branch": ticket.branch, "is_active": 1},
		"template_text",
	)
	if not template_text:
		template_text = (
			"KOT: {order_number}\n"
			"Type: {order_type}\n"
			"Table: {table}\n"
			"Station: {station}\n"
			"Items:\n{items}\n"
		)
	text = template_text.format(
		order_number=payload.get("order_number") or ticket.restaurant_order,
		order_type=payload.get("order_type") or "",
		table=payload.get("table") or "-",
		station=ticket.kitchen_station or "-",
		items=items_text,
	)
	return {"ticket": ticket.name, "preview": text}


@frappe.whitelist()
def send_kot_to_printer(ticket_name: str):
	ticket = frappe.get_doc("Kitchen Ticket", ticket_name)
	preview = get_kot_print_preview(ticket_name).get("preview")
	job = frappe.new_doc("Kitchen Print Job")
	job.kitchen_ticket = ticket.name
	job.kitchen_printer = ticket.kitchen_printer
	job.status = "Printed"
	job.payload = preview
	job.printed_on = frappe.utils.now_datetime()
	job.company = ticket.company
	job.branch = ticket.branch
	job.insert(ignore_permissions=True)
	ticket.ticket_status = "Printed"
	ticket.save(ignore_permissions=True)
	frappe.publish_realtime("restaurant_kds_update", {"ticket": ticket.name, "status": "Printed", "order": ticket.restaurant_order})
	return {"ticket": ticket.name, "print_job": job.name, "status": "Printed"}

