frappe.pages["restaurant-pos"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Restaurant POS"),
		single_column: true,
	});

	const $body = $(`
		<div class="restaurant-pos p-4">
			<div class="mb-3 d-flex gap-2">
				<button class="btn btn-primary btn-sm" id="refresh-orders">${__("Refresh Orders")}</button>
				<button class="btn btn-success btn-sm" id="new-order">${__("New Dine-in Order")}</button>
				<button class="btn btn-warning btn-sm" id="split-order">${__("Split Bill")}</button>
				<button class="btn btn-info btn-sm" id="transfer-order">${__("Transfer Table")}</button>
			</div>
			<div class="row">
				<div class="col-md-4">
					<div class="mb-2"><strong>${__("Open Orders")}</strong></div>
					<div id="orders-list" class="small text-muted">${__("Loading...")}</div>
				</div>
				<div class="col-md-8">
					<div class="mb-2"><strong>${__("Menu Catalog")}</strong></div>
					<div id="menu-catalog" class="small text-muted">${__("Loading menu...")}</div>
					<hr class="my-3">
					<div class="mb-2"><strong>${__("Table Map")}</strong></div>
					<div id="table-map" class="small text-muted">${__("Loading tables...")}</div>
				</div>
			</div>
		</div>
	`);
	$(page.body).append($body);
	let currentOrder = null;
	const renderOrders = (orders) => {
		if (!orders.length) {
			$body.find("#orders-list").html(`<div class="text-muted">${__("No open POS orders.")}</div>`);
			return;
		}
		const rows = orders
			.map(
				(o) => `
			<div class="border rounded p-2 mb-2 ${currentOrder === o.name ? "border-primary" : ""}" data-order="${o.name}">
				<div><strong>${o.name}</strong> - ${o.order_type} - ${o.status}</div>
				<div>${__("Table")}: ${o.table || "-"}, ${__("Customer")}: ${o.customer_profile || "-"}</div>
				<div>${__("Total")}: ${format_currency(o.total_amount || 0)}</div>
			</div>`
			)
			.join("");
		$body.find("#orders-list").html(rows);
	};

	const loadOrders = () => {
		frappe.call({
			method: "omnexa_restaurant.api.get_open_pos_orders",
			callback: (r) => {
				const orders = r.message || [];
				renderOrders(orders);
				if (!currentOrder && orders.length) currentOrder = orders[0].name;
			},
		});
	};

	const loadCatalog = () => {
		frappe.call({
			method: "omnexa_restaurant.api.get_pos_catalog",
			callback: (r) => {
				const payload = r.message || {};
				const categories = payload.categories || [];
				const map = payload.items_by_category || {};
				const html = categories
					.map((cat) => {
						const items = (map[cat] || [])
							.map(
								(i) => `
							<button class="btn btn-outline-secondary btn-sm m-1 pos-item" data-item="${i.name}">
								${i.item_name} (${format_currency(i.default_price || 0)})
							</button>`
							)
							.join("");
						return `<div class="mb-2"><div><strong>${cat}</strong></div><div>${items}</div></div>`;
					})
					.join("");
				$body.find("#menu-catalog").html(html || `<div class="text-muted">${__("No menu items.")}</div>`);
			},
		});
	};

	const loadTableMap = () => {
		frappe.call({
			method: "omnexa_restaurant.api.get_table_map",
			callback: (r) => {
				const payload = r.message || {};
				const floors = payload.floors || [];
				const map = payload.tables_by_floor || {};
				const html = floors
					.map((f) => {
						const tables = (map[f.name] || [])
							.map((t) => {
								const color =
									t.status === "Available"
										? "btn-success"
										: t.status === "Occupied"
											? "btn-danger"
											: t.status === "Reserved"
												? "btn-warning"
												: "btn-secondary";
								return `<button class="btn btn-xs ${color} m-1 pos-table" data-table="${t.name}">${t.table_number} (${t.status})</button>`;
							})
							.join("");
						return `<div class="mb-2"><div><strong>${f.floor_name}</strong></div><div>${tables}</div></div>`;
					})
					.join("");
				$body.find("#table-map").html(html || `<div class="text-muted">${__("No tables found.")}</div>`);
			},
		});
	};

	$body.on("click", "#refresh-orders", loadOrders);
	$body.on("click", "#new-order", () => {
		frappe.call({
			method: "omnexa_restaurant.api.create_pos_order",
			args: { order_type: "Dine-in" },
			callback: (r) => {
				currentOrder = r.message.order_name;
				frappe.show_alert({ message: __("Order {0} created", [currentOrder]), indicator: "green" });
				loadOrders();
			},
		});
	});
	$body.on("click", "#split-order", () => {
		if (!currentOrder) {
			frappe.msgprint(__("Select an order first."));
			return;
		}
		frappe.call({
			method: "omnexa_restaurant.api.get_order_items",
			args: { order_name: currentOrder },
			callback: (r) => {
				const items = r.message || [];
				if (!items.length) {
					frappe.msgprint(__("No items available to split."));
					return;
				}
				frappe.prompt(
					[
						{
							fieldname: "row_name",
							label: __("Item Row"),
							fieldtype: "Select",
							options: items.map((i) => `${i.row_name}:${i.menu_item} x ${i.quantity}`).join("\n"),
							reqd: 1,
						},
						{
							fieldname: "split_qty",
							label: __("Split Quantity"),
							fieldtype: "Float",
							default: 1,
							reqd: 1,
						},
					],
					(values) => {
						const rowName = (values.row_name || "").split(":")[0];
						frappe.call({
							method: "omnexa_restaurant.api.split_bill_by_quantity",
							args: { order_name: currentOrder, row_name: rowName, quantity: values.split_qty },
							callback: () => loadOrders(),
						});
					},
					__("Split Bill"),
					__("Split")
				);
			},
		});
	});
	$body.on("click", "#transfer-order", () => {
		if (!currentOrder) {
			frappe.msgprint(__("Select an order first."));
			return;
		}
		frappe.prompt(
			[
				{
					fieldname: "new_table",
					label: __("New Table"),
					fieldtype: "Link",
					options: "Restaurant Table",
					reqd: 1,
				},
			],
			(values) => {
				frappe.call({
					method: "omnexa_restaurant.api.transfer_order",
					args: { order_name: currentOrder, new_table: values.new_table },
					callback: () => {
						loadOrders();
						loadTableMap();
					},
				});
			},
			__("Transfer Order"),
			__("Transfer")
		);
	});
	$body.on("click", ".pos-item", function () {
		const menuItem = $(this).data("item");
		if (!currentOrder) {
			frappe.msgprint(__("Create or select an order first."));
			return;
		}
		frappe.call({
			method: "omnexa_restaurant.api.add_item_to_order",
			args: { order_name: currentOrder, menu_item: menuItem, qty: 1 },
			callback: () => loadOrders(),
		});
	});
	$body.on("click", ".pos-table", function () {
		const table = $(this).data("table");
		if (!currentOrder) return;
		frappe.call({
			method: "omnexa_restaurant.api.transfer_order",
			args: { order_name: currentOrder, new_table: table },
			callback: () => {
				loadOrders();
				loadTableMap();
			},
		});
	});
	$body.on("click", ".border.rounded", function () {
		const name = $(this).data("order");
		if (!name) return;
		currentOrder = name;
		$body.find(".border.rounded").removeClass("border-primary");
		$(this).addClass("border-primary");
	});

	loadOrders();
	loadCatalog();
	loadTableMap();
};

