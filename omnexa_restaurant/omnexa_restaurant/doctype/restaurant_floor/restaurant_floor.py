import frappe
from frappe import _
from frappe.model.document import Document


class RestaurantFloor(Document):
	def validate(self):
		branch_company = frappe.db.get_value("Branch", self.branch, "company")
		if branch_company and branch_company != self.company:
			frappe.throw(_("Branch belongs to another company."), title=_("Floor"))

