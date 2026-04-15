frappe.pages["kitchen-display"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Kitchen Display"),
		single_column: true,
	});

	const $body = $(`
		<div class="kds p-4">
			<div class="mb-3 d-flex gap-2 align-items-center">
				<label class="mb-0">${__("Station")}:</label>
				<input type="text" class="form-control form-control-sm" id="station-filter" style="max-width: 260px;" placeholder="${__("Kitchen Station name")}">
				<button class="btn btn-primary btn-sm" id="refresh-kds">${__("Refresh")}</button>
			</div>
			<div id="kds-list" class="small text-muted">${__("Loading...")}</div>
		</div>
	`);
	$(page.body).append($body);

	const statusButtons = (name, status) => `
		<div class="mt-2 d-flex gap-1">
			<button class="btn btn-xs ${status === "Pending" ? "btn-primary" : "btn-default"} kds-status" data-ticket="${name}" data-status="Pending">${__("Pending")}</button>
			<button class="btn btn-xs ${status === "Preparing" ? "btn-warning" : "btn-default"} kds-status" data-ticket="${name}" data-status="Preparing">${__("Preparing")}</button>
			<button class="btn btn-xs ${status === "Ready" ? "btn-success" : "btn-default"} kds-status" data-ticket="${name}" data-status="Ready">${__("Ready")}</button>
			<button class="btn btn-xs btn-default kds-preview" data-ticket="${name}">${__("KOT Preview")}</button>
			<button class="btn btn-xs btn-primary kds-print" data-ticket="${name}">${__("Send to Printer")}</button>
		</div>
	`;

	const render = (tickets) => {
		if (!tickets.length) {
			$body.find("#kds-list").html(`<div class="text-muted">${__("No open kitchen tickets.")}</div>`);
			return;
		}
		const html = tickets
			.map((t) => {
				let payload = {};
				try {
					payload = JSON.parse(t.ticket_payload || "{}");
				} catch (e) {
					payload = {};
				}
				const items = (payload.items || [])
					.map((i) => `<li>${i.menu_item} x ${i.quantity}${i.notes ? ` - ${i.notes}` : ""}</li>`)
					.join("");
				return `
					<div class="border rounded p-2 mb-2">
						<div><strong>${t.name}</strong> - ${__("Order")}: ${t.restaurant_order}</div>
						<div>${__("Station")}: ${t.kitchen_station || "-"}, ${__("Status")}: ${t.ticket_status}</div>
						<ul class="mb-1">${items}</ul>
						${statusButtons(t.name, t.ticket_status)}
					</div>
				`;
			})
			.join("");
		$body.find("#kds-list").html(html);
	};

	const load = () => {
		frappe.call({
			method: "omnexa_restaurant.api.get_kitchen_tickets",
			args: { station: $body.find("#station-filter").val() || null },
			callback: (r) => render(r.message || []),
		});
	};

	$body.on("click", "#refresh-kds", load);
	$body.on("click", ".kds-status", function () {
		const ticket = $(this).data("ticket");
		const status = $(this).data("status");
		frappe.call({
			method: "omnexa_restaurant.api.update_kitchen_ticket_status",
			args: { ticket_name: ticket, status },
			callback: () => load(),
		});
	});
	$body.on("click", ".kds-preview", function () {
		const ticket = $(this).data("ticket");
		frappe.call({
			method: "omnexa_restaurant.api.get_kot_print_preview",
			args: { ticket_name: ticket },
			callback: (r) => {
				const text = (r.message && r.message.preview) || "";
				frappe.msgprint(`<pre style="white-space:pre-wrap;">${frappe.utils.escape_html(text)}</pre>`, __("KOT Preview"));
			},
		});
	});
	$body.on("click", ".kds-print", function () {
		const ticket = $(this).data("ticket");
		frappe.call({
			method: "omnexa_restaurant.api.send_kot_to_printer",
			args: { ticket_name: ticket },
			callback: () => load(),
		});
	});

	frappe.realtime.on("restaurant_kds_update", () => load());
	load();
};

