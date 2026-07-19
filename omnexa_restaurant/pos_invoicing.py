# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Restaurant POS → Sales Invoice → e-invoice / ZATCA bridge."""

from __future__ import annotations

from typing import Any

import frappe
from frappe import _
from frappe.utils import flt, getdate, nowdate

from omnexa_restaurant.pos_catalog import menu_item_unit_cost, resolve_effective_price


WALKIN_CUSTOMER_NAME = "Restaurant Walk-in Customer"


def ensure_walkin_customer(company: str) -> str:
	existing = frappe.db.get_value("Customer", {"customer_name": WALKIN_CUSTOMER_NAME, "company": company}, "name")
	if existing:
		return existing
	meta = frappe.get_meta("Customer")
	payload: dict[str, Any] = {
		"doctype": "Customer",
		"customer_name": WALKIN_CUSTOMER_NAME,
		"company": company,
	}
	if meta.has_field("status"):
		payload["status"] = "Active"
	if meta.has_field("customer_type"):
		payload["customer_type"] = "Individual"
	if meta.has_field("customer_group"):
		group = None
		if frappe.db.exists("DocType", "Selling Settings"):
			group = frappe.db.get_single_value("Selling Settings", "customer_group")
		payload["customer_group"] = group or "Individual"
	if meta.has_field("territory"):
		territory = None
		if frappe.db.exists("DocType", "Selling Settings"):
			territory = frappe.db.get_single_value("Selling Settings", "territory")
		payload["territory"] = territory or "All Territories"
	customer = frappe.get_doc(payload)
	customer.insert(ignore_permissions=True)
	return customer.name


def ensure_erp_item_for_menu_item(menu_item) -> str:
	"""Create or return ErpGenex Item for a menu item."""
	if menu_item.erp_item and frappe.db.exists("Item", menu_item.erp_item):
		return menu_item.erp_item
	item_code = (menu_item.item_code or menu_item.name).strip()
	if frappe.db.exists("Item", item_code):
		return item_code
	item_group = "Services" if menu_item.item_type == "Service" else "Products"
	if not frappe.db.exists("Item Group", item_group):
		item_group = frappe.db.get_value("Item Group", {}, "name") or "All Item Groups"
	is_stock = 1 if menu_item.item_type in ("Product", "Raw Material") else 0
	is_sales = 1 if menu_item.item_type in ("Product", "Service", "Bundle") else 0
	item = frappe.get_doc(
		{
			"doctype": "Item",
			"item_code": item_code,
			"item_name": menu_item.item_name,
			"item_group": item_group,
			"stock_uom": "Nos",
			"is_stock_item": is_stock,
			"is_sales_item": is_sales,
			"is_purchase_item": menu_item.item_type == "Raw Material",
			"description": menu_item.description or menu_item.item_name,
			"standard_rate": flt(menu_item.default_price),
		}
	)
	item.insert(ignore_permissions=True)
	return item.name


def _resolve_item_code(menu_item_name: str) -> str:
	menu = frappe.get_doc("Menu Item", menu_item_name)
	if menu.erp_item and frappe.db.exists("Item", menu.erp_item):
		return menu.erp_item
	return ensure_erp_item_for_menu_item(menu)


def _tax_template_for_branch(branch: str | None) -> str | None:
	if not branch:
		return None
	country = frappe.db.get_value("Branch", branch, "country_code") or ""
	if country in ("SA", "SAU", "Saudi Arabia"):
		for title in ("VAT 15% - S", "VAT 15%", "Standard VAT 15%"):
			name = frappe.db.get_value("Sales Taxes and Charges Template", {"title": title, "company": frappe.defaults.get_user_default("Company")}, "name")
			if name:
				return name
	return None


def create_sales_invoice_from_restaurant_order(order_name: str) -> dict[str, Any]:
	order = frappe.get_doc("Restaurant Order", order_name)
	if order.sales_invoice and frappe.db.exists("Sales Invoice", order.sales_invoice):
		return {"sales_invoice": order.sales_invoice, "created": False}

	customer = order.customer or ensure_walkin_customer(order.company)
	si = frappe.new_doc("Sales Invoice")
	si.company = order.company
	si.customer = customer
	si.posting_date = nowdate()
	si.due_date = nowdate()
	si.is_pos = 1
	si.update_stock = 0
	if hasattr(si, "branch"):
		si.branch = order.branch

	tax_template = _tax_template_for_branch(order.branch)
	if tax_template and hasattr(si, "taxes_and_charges"):
		si.taxes_and_charges = tax_template

	for row in order.items:
		item_code = _resolve_item_code(row.menu_item)
		menu = frappe.db.get_value("Menu Item", row.menu_item, ["item_name", "classification_code"], as_dict=True) or {}
		si.append(
			"items",
			{
				"item_code": item_code,
				"item_name": menu.get("item_name") or item_code,
				"description": menu.get("item_name") or item_code,
				"qty": flt(row.quantity),
				"rate": flt(row.price),
				"conversion_factor": 1,
				"uom": frappe.db.get_value("Item", item_code, "stock_uom") or "Nos",
			},
		)

	si.flags.ignore_permissions = True
	si.insert()
	si.submit()

	einvoice_result = dispatch_einvoice_for_sales_invoice(si)
	frappe.db.set_value(
		"Restaurant Order",
		order.name,
		{
			"sales_invoice": si.name,
			"customer": customer,
			"einvoice_status": einvoice_result.get("status") or einvoice_result.get("authority_status") or "Submitted",
		},
		update_modified=False,
	)
	return {
		"sales_invoice": si.name,
		"created": True,
		"einvoice": einvoice_result,
	}


def dispatch_einvoice_for_sales_invoice(si) -> dict[str, Any]:
	"""Dispatch tax for branch country via omnexa_einvoice when installed."""
	if isinstance(si, str):
		si = frappe.get_doc("Sales Invoice", si)
	if "omnexa_einvoice" not in frappe.get_installed_apps():
		return {"status": "skipped", "reason": "omnexa_einvoice not installed"}
	try:
		from omnexa_einvoice.tax_engine.dispatch import dispatch_tax_for_document

		return dispatch_tax_for_document("Sales Invoice", si.name, branch=getattr(si, "branch", None))
	except Exception as exc:
		frappe.log_error(frappe.get_traceback(), "Restaurant POS e-invoice dispatch")
		return {"status": "error", "message": str(exc)}


def get_einvoice_receipt_context(order_name: str) -> dict[str, Any]:
	"""QR and tax metadata for thermal receipt."""
	order = frappe.get_doc("Restaurant Order", order_name)
	out: dict[str, Any] = {"qr_image_base64": "", "uuid": "", "sales_invoice": order.sales_invoice or ""}
	if not order.sales_invoice:
		return out
	if "omnexa_einvoice" not in frappe.get_installed_apps():
		return out
	try:
		from omnexa_einvoice.einvoice_print.context import get_sales_invoice_print_context

		ctx = get_sales_invoice_print_context(order.sales_invoice)
		tax = ctx.get("tax") or {}
		out["qr_image_base64"] = tax.get("qr_image_base64") or ""
		out["uuid"] = tax.get("uuid") or ""
		out["authority_status"] = tax.get("authority_status") or tax.get("status") or ""
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Restaurant receipt einvoice context")
	return out


def line_cost_for_menu_item(menu_item_name: str) -> float:
	return menu_item_unit_cost(menu_item_name)


def line_price_for_menu_item(menu_item_name: str, qty: float = 1) -> float:
	base = frappe.db.get_value("Menu Item", menu_item_name, "default_price") or 0
	return resolve_effective_price(menu_item_name, flt(base), qty=qty)
