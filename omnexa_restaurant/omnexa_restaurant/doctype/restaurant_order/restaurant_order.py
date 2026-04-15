from frappe.model.document import Document
from frappe.utils import flt


class RestaurantOrder(Document):
	def validate(self):
		total = 0
		total_cost = 0
		total_tips = 0
		total_paid = 0
		for row in self.items:
			row.line_amount = flt(row.quantity) * flt(row.price)
			row.line_cost = flt(row.quantity) * flt(row.cost)
			total += flt(row.line_amount)
			total_cost += flt(row.line_cost)
		for payment in self.payments:
			total_tips += flt(payment.tips_amount)
			total_paid += flt(payment.amount) + flt(payment.tips_amount)
		self.total_amount = flt(total, 2)
		self.cost_amount = flt(total_cost, 2)
		self.tips_amount = flt(total_tips, 2)
		self.profit_amount = flt(self.total_amount - self.cost_amount + self.tips_amount, 2)
		self.paid_amount = flt(total_paid, 2)
		self.due_amount = flt(self.total_amount + self.tips_amount - self.paid_amount, 2)

	def on_submit(self):
		from omnexa_restaurant.api import generate_kitchen_tickets

		generate_kitchen_tickets(self.name)

