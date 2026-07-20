# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""In-POS menu item / category / offer management APIs."""

from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _
from frappe.utils import cint, flt

from omnexa_restaurant.pos_catalog import (
	POS_ITEM_TYPES,
	get_active_offers,
	menu_item_existing_fields,
	menu_item_has_field,
	serialize_menu_item,
)
from omnexa_restaurant.pos_invoicing import ensure_erp_item_for_menu_item


def _default_company_branch() -> tuple[str | None, str | None]:
	company = frappe.defaults.get_user_default("Company")
	branch = frappe.defaults.get_user_default("Branch")
	return company, branch


@frappe.whitelist()
def get_menu_categories(company: str | None = None, branch: str | None = None):
	company = company or _default_company_branch()[0]
	branch = branch or _default_company_branch()[1]
	filters: dict[str, Any] = {"is_active": 1
	}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	return frappe.get_all(
		"Menu Category",
		filters=filters,
		fields=["name", "category_name", "name_ar", "sort_order"],
		order_by="sort_order asc, category_name asc",
	)


@frappe.whitelist()
def get_menu_items_for_manager(
	item_type: str | None = None,
	company: str | None = None,
	branch: str | None = None,
	search: str | None = None,
):
	company, branch = company or _default_company_branch()[0], branch or _default_company_branch()[1]
	filters: dict[str, Any] = {}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	has_item_type = menu_item_has_field("item_type")
	if has_item_type and item_type and item_type != "All":
		filters["item_type"] = item_type
	fields = menu_item_existing_fields([
		"name",
		"item_code",
		"item_name",
		"item_type",
		"category",
		"menu_category",
		"default_price",
		"image",
		"description",
		"is_active",
		"erp_item",
		"kitchen_station",
		"classification_code",
		"is_manufactured",
	])
	rows = frappe.get_all(
		"Menu Item",
		filters=filters,
		fields=fields,
		order_by="item_name asc",
		limit_page_length=500,
	)
	if search:
		term = search.strip().lower()
		rows = [r for r in rows if term in (r.item_name or "").lower() or term in (r.item_code or "").lower()]
	offers = get_active_offers(company, branch)
	return [serialize_menu_item(r, offers) for r in rows]


@frappe.whitelist()
def get_menu_item_detail(name: str):
	doc = frappe.get_doc("Menu Item", name)
	recipe = frappe.db.get_value(
		"Restaurant Recipe",
		{"menu_item": name, "is_active": 1
	},
		["name", "yield_qty", "preparation_time_mins"],
		as_dict=True,
	)
	ingredients = []
	if recipe and recipe.name:
		ingredients = frappe.get_all(
			"Restaurant Recipe Item",
			filters={"parent": recipe.name
	},
			fields=["ingredient_item", "qty", "waste_percentage"],
		)
	return {
		**serialize_menu_item(doc.as_dict()),
		"bundle_items": [
			{"menu_item": r.menu_item, "item_name": r.item_name, "quantity": r.quantity
	}
			for r in (doc.bundle_items or [])
		],
		"recipe": recipe,
		"ingredients": ingredients,
		"company": doc.company,
		"branch": doc.branch,
		"is_active": doc.is_active
	}


@frappe.whitelist()
def save_menu_item(payload_json: str):
	data = frappe.parse_json(payload_json) or {}
	company, branch = data.get("company") or _default_company_branch()[0], data.get("branch") or _default_company_branch()[1]
	if not company or not branch:
		frappe.throw(_("Company and Branch are required."))

	name = data.get("name")
	if name and frappe.db.exists("Menu Item", name):
		doc = frappe.get_doc("Menu Item", name)
	else:
		doc = frappe.new_doc("Menu Item")

	doc.item_code = (data.get("item_code") or data.get("item_name") or "").strip()
	doc.item_name = (data.get("item_name") or doc.item_code).strip()
	doc.item_type = data.get("item_type") or "Product"
	if doc.item_type not in ("Product", "Service", "Raw Material", "Bundle"):
		frappe.throw(_("Invalid item type."))
	doc.category = data.get("category") or ""
	doc.menu_category = data.get("menu_category") or None
	doc.default_price = flt(data.get("default_price"))
	doc.description = data.get("description") or ""
	doc.kitchen_station = data.get("kitchen_station") or None
	doc.classification_code = data.get("classification_code") or ""
	doc.is_manufactured = cint(data.get("is_manufactured"))
	doc.is_active = cint(data.get("is_active", 1))
	doc.company = company
	doc.branch = branch
	if data.get("image"):
		doc.image = data.get("image")

	doc.bundle_items = []
	for row in data.get("bundle_items") or []:
		if not row.get("menu_item"):
			continue
		doc.append(
			"bundle_items",
			{"menu_item": row.get("menu_item"), "quantity": flt(row.get("quantity") or 1)
	},
		)

	doc.flags.ignore_permissions = True
	if name and frappe.db.exists("Menu Item", name):
		doc.save()
	else:
		doc.insert()

	if doc.item_type in ("Product", "Service", "Bundle"):
		ensure_erp_item_for_menu_item(doc)
		if not doc.erp_item:
			doc.reload()

	_save_recipe_from_payload(doc.name, data)
	return get_menu_item_detail(doc.name)


def _save_recipe_from_payload(menu_item_name: str, data: dict[str, Any]) -> None:
	ingredients = data.get("ingredients") or []
	if not ingredients:
		return
	recipe_name = frappe.db.get_value("Restaurant Recipe", {"menu_item": menu_item_name
	}, "name")
	if recipe_name:
		recipe = frappe.get_doc("Restaurant Recipe", recipe_name)
	else:
		recipe = frappe.new_doc("Restaurant Recipe")
		recipe.menu_item = menu_item_name
		recipe.company = data.get("company")
		recipe.branch = data.get("branch")
	recipe.yield_qty = flt(data.get("yield_qty") or recipe.yield_qty or 1)
	recipe.preparation_time_mins = cint(data.get("preparation_time_mins") or recipe.preparation_time_mins or 0)
	recipe.is_active = 1
	recipe.ingredients = []
	for row in ingredients:
		if not row.get("ingredient_item"):
			continue
		recipe.append(
			"ingredients",
			{
				"ingredient_item": row.get("ingredient_item"),
				"qty": flt(row.get("qty") or 1),
				"waste_percentage": flt(row.get("waste_percentage") or 0)
	},
		)
	recipe.flags.ignore_permissions = True
	if recipe.get("__islocal") or not recipe.name:
		recipe.insert()
	else:
		recipe.save()


@frappe.whitelist()
def toggle_menu_item_active(name: str, is_active: int | str = 1):
	frappe.db.set_value("Menu Item", name, "is_active", cint(is_active))
	return {"name": name, "is_active": cint(is_active)
	}


@frappe.whitelist()
def save_menu_category(payload_json: str):
	data = frappe.parse_json(payload_json) or {}
	company, branch = data.get("company") or _default_company_branch()[0], data.get("branch") or _default_company_branch()[1]
	name = data.get("name")
	if name and frappe.db.exists("Menu Category", name):
		doc = frappe.get_doc("Menu Category", name)
	else:
		doc = frappe.new_doc("Menu Category")
	doc.category_name = (data.get("category_name") or "").strip()
	doc.name_ar = data.get("name_ar") or doc.category_name
	doc.sort_order = cint(data.get("sort_order"))
	doc.company = company
	doc.branch = branch
	doc.is_active = cint(data.get("is_active", 1))
	doc.flags.ignore_permissions = True
	doc.save() if doc.name else doc.insert()
	return doc.as_dict()


@frappe.whitelist()
def get_restaurant_offers(company: str | None = None, branch: str | None = None):
	company, branch = company or _default_company_branch()[0], branch or _default_company_branch()[1]
	filters: dict[str, Any] = {}
	if company:
		filters["company"] = company
	if branch:
		filters["branch"] = branch
	return frappe.get_all(
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
			"is_active",
		],
		order_by="modified desc",
	)


@frappe.whitelist()
def save_restaurant_offer(payload_json: str):
	data = frappe.parse_json(payload_json) or {}
	company, branch = data.get("company") or _default_company_branch()[0], data.get("branch") or _default_company_branch()[1]
	name = data.get("name")
	doc = frappe.get_doc("Restaurant Offer", name) if name and frappe.db.exists("Restaurant Offer", name) else frappe.new_doc("Restaurant Offer")
	doc.offer_name = (data.get("offer_name") or "").strip()
	doc.offer_type = data.get("offer_type") or "Percent Discount"
	doc.menu_item = data.get("menu_item") or None
	doc.discount_percent = flt(data.get("discount_percent"))
	doc.fixed_price = flt(data.get("fixed_price"))
	doc.min_quantity = flt(data.get("min_quantity") or 1)
	doc.valid_from = data.get("valid_from") or None
	doc.valid_to = data.get("valid_to") or None
	doc.company = company
	doc.branch = branch
	doc.is_active = cint(data.get("is_active", 1))
	doc.flags.ignore_permissions = True
	doc.save() if doc.name else doc.insert()
	return doc.as_dict()
