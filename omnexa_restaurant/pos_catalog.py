# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""POS catalog pricing, offers, and recipe cost helpers."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import flt, getdate, today


POS_ITEM_TYPES = ("Product", "Service", "Bundle")


def menu_item_image_url(image: str | None) -> str | None:
	if not image:
		return None
	if image.startswith(("http://", "https://", "/")):
		return image
	return frappe.utils.get_url(image)


def menu_item_unit_cost(menu_item_name: str) -> float:
	recipe_name = frappe.db.get_value(
		"Restaurant Recipe",
		{"menu_item": menu_item_name, "is_active": 1},
		"name",
	)
	if not recipe_name:
		return 0.0
	recipe = frappe.get_doc("Restaurant Recipe", recipe_name)
	total = 0.0
	for row in recipe.ingredients:
		rate = frappe.db.get_value("Item", row.ingredient_item, "valuation_rate") or 0
		waste = 1 + flt(row.waste_percentage) / 100
		total += flt(row.qty) * flt(rate) * waste
	yield_qty = flt(recipe.yield_qty) or 1
	return flt(total / yield_qty, 2)


def get_active_offers(company: str | None = None, branch: str | None = None) -> list[dict[str, Any]]:
	filters: dict[str, Any] = {"is_active": 1}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	offers = frappe.get_all(
		"Restaurant Offer",
		filters=filters,
		fields=[
			"name",
			"offer_name",
			"offer_type",
			"menu_item",
			"discount_percent",
			"fixed_price",
			"min_quantity",
			"valid_from",
			"valid_to",
		],
	)
	today_date = getdate(today())
	active: list[dict[str, Any]] = []
	for offer in offers:
		if offer.valid_from and getdate(offer.valid_from) > today_date:
			continue
		if offer.valid_to and getdate(offer.valid_to) < today_date:
			continue
		active.append(offer)
	return active


def resolve_effective_price(
	menu_item_name: str,
	base_price: float,
	*,
	qty: float = 1,
	offers: list[dict[str, Any]] | None = None,
) -> float:
	price = flt(base_price)
	if not offers:
		menu = frappe.db.get_value("Menu Item", menu_item_name, ["company", "branch"], as_dict=True) or {}
		offers = get_active_offers(menu.get("company"), menu.get("branch"))
	best = price
	for offer in offers:
		if offer.menu_item and offer.menu_item != menu_item_name:
			continue
		if flt(qty) < flt(offer.min_quantity or 1):
			continue
		if offer.offer_type == "Fixed Price" and flt(offer.fixed_price) >= 0:
			candidate = flt(offer.fixed_price)
		elif offer.offer_type == "Percent Discount" and flt(offer.discount_percent):
			candidate = flt(price * (1 - flt(offer.discount_percent) / 100), 2)
		else:
			continue
		if candidate < best:
			best = candidate
	return flt(best, 2)


def expand_bundle_lines(menu_item_name: str, qty: float = 1) -> list[dict[str, Any]]:
	"""Kitchen / costing view of bundle components."""
	menu = frappe.get_doc("Menu Item", menu_item_name)
	if menu.item_type != "Bundle":
		return [{"menu_item": menu_item_name, "quantity": qty, "item_name": menu.item_name}]
	lines: list[dict[str, Any]] = []
	for row in menu.bundle_items or []:
		child = frappe.db.get_value("Menu Item", row.menu_item, "item_name") or row.menu_item
		lines.append(
			{
				"menu_item": row.menu_item,
				"quantity": flt(row.quantity) * flt(qty),
				"item_name": child,
			}
		)
	return lines or [{"menu_item": menu_item_name, "quantity": qty, "item_name": menu.item_name}]


def serialize_menu_item(row: dict[str, Any], offers: list[dict[str, Any]] | None = None) -> dict[str, Any]:
	base = flt(row.get("default_price"))
	effective = resolve_effective_price(row["name"], base, offers=offers)
	return {
		"name": row["name"],
		"item_code": row.get("item_code"),
		"item_name": row.get("item_name"),
		"item_type": row.get("item_type") or "Product",
		"category": row.get("category") or "General",
		"menu_category": row.get("menu_category"),
		"default_price": base,
		"effective_price": effective,
		"has_offer": effective < base,
		"image": menu_item_image_url(row.get("image")),
		"description": row.get("description") or "",
		"kitchen_station": row.get("kitchen_station"),
		"erp_item": row.get("erp_item"),
		"classification_code": row.get("classification_code"),
		"is_manufactured": row.get("is_manufactured"),
	}
