import frappe
from frappe.utils import flt, nowdate


def create_tourism_service_order_from_restaurant_order(order_doc):
	"""
	Create a Tourism Service Order (and therefore a Charge Entry / folio trail) from a submitted Restaurant Order.

	This integration is intentionally best-effort and only runs when:
	- omnexa_tourism is installed
	- the Tourism DocTypes exist in the database
	- the Restaurant Order is marked as "Charge to Room" and has a Tourism Booking.
	"""
	if not order_doc:
		return None

	if not getattr(order_doc, "charge_to_room", 0):
		return None
	if not getattr(order_doc, "tourism_booking", None):
		return None

	if "omnexa_tourism" not in frappe.get_installed_apps():
		return None
	if not frappe.db.exists("DocType", "Tourism Service Order"):
		return None

	if getattr(order_doc, "tourism_service_order", None) and frappe.db.exists(
		"Tourism Service Order", order_doc.tourism_service_order
	):
		return order_doc.tourism_service_order

	booking = frappe.db.get_value(
		"Tourism Booking",
		order_doc.tourism_booking,
		["customer", "company", "branch", "hotel", "unit", "status", "guest_folio"],
		as_dict=True,
	)
	if not booking:
		return None
	if booking.get("company") != order_doc.company or booking.get("branch") != order_doc.branch:
		return None

	# Only allow charging to room when the guest is currently in-house.
	if booking.get("status") not in {"Checked In"}:
		return None

	amount = flt(order_doc.total_amount) + flt(order_doc.tips_amount)
	if not amount:
		return None

	service_order = frappe.get_doc(
		{
			"doctype": "Tourism Service Order",
			"booking": order_doc.tourism_booking,
			"customer": booking.get("customer"),
			"company": order_doc.company,
			"branch": order_doc.branch,
			"hotel": booking.get("hotel"),
			"room_unit": booking.get("unit"),
			"service_category": "Restaurant",
			"source_app": "Restaurant",
			"service_date": nowdate(),
			"reference_doctype": "Restaurant Order",
			"reference_name": order_doc.name,
			"description": f"Restaurant order {order_doc.name
	}",
			"quantity": 1,
			"rate": amount,
			"status": "Billed"
	}
	)
	service_order.insert(ignore_permissions=True)

	frappe.db.set_value(
		"Restaurant Order",
		order_doc.name,
		{
			"tourism_service_order": service_order.name,
			"tourism_guest_folio": service_order.folio
	},
		update_modified=False,
	)
	return service_order.name

