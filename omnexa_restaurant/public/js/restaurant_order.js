frappe.ui.form.on("Restaurant Order", {
	refresh(frm) {
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__("Generate Kitchen Tickets"), () => {
				frappe.call({
					method: "omnexa_restaurant.api.generate_kitchen_tickets",
					args: { order_name: frm.doc.name },
					callback: () => frappe.msgprint(__("Kitchen tickets generated.")),
				});
			});
			frm.add_custom_button(__("Hold/Resume"), () => {
				frappe.call({
					method: "omnexa_restaurant.api.toggle_hold_order",
					args: { order_name: frm.doc.name },
					callback: () => frm.reload_doc(),
				});
			});
		}
	},
	order_type(frm) {
		frm.toggle_display(["delivery_driver", "delivery_status", "eta_mins"], frm.doc.order_type === "Delivery");
	},
});

