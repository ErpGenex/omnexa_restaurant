frappe.provide("omnexa_restaurant.pos");

omnexa_restaurant.pos = {
	FOOD_GRADIENTS: [
		"linear-gradient(135deg,#f6d365,#fda085)",
		"linear-gradient(135deg,#a8edea,#fed6e3)",
		"linear-gradient(135deg,#ffecd2,#fcb69f)",
		"linear-gradient(135deg,#d4fc79,#96e6a1)",
		"linear-gradient(135deg,#fbc2eb,#a6c1ee)",
		"linear-gradient(135deg,#fdcbf1,#e6dee9)",
		"linear-gradient(135deg,#a1c4fd,#c2e9fb)",
		"linear-gradient(135deg,#fddb92,#d1fdff)",
	],
	CATEGORY_AR: {
		General: "عام",
		Appetizers: "المقبلات",
		"Main Dishes": "الأطباق الرئيسية",
		"Side Dishes": "الأطباق الجانبية",
		Drinks: "المشروبات",
		Desserts: "الحلويات",
		المقبلات: "المقبلات",
		"الأطباق الرئيسية": "الأطباق الرئيسية",
		"الأطباق الجانبية": "الأطباق الجانبية",
		المشروبات: "المشروبات",
		الحلويات: "الحلويات",
	},

	init(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Restaurant POS"),
			single_column: true,
		});
		$(this.page.page_container).addClass("rest-pos-page");
		this.state = {
			catalog: { categories: [], items_by_category: {} },
			activeCategory: __("All"),
			search: "",
			currentOrder: null,
			orderDetail: null,
			customer: null,
		};
		this.render_shell();
		this.bind_events();
		omnexa_restaurant.product_manager.init(this);
		this.bootstrap();
	},

	render_shell() {
		const cashier = frappe.session.user_fullname || frappe.session.user;
		const initial = (cashier || "A").trim()[0] || "A";
		const $root = $(`
			<div class="rest-pos" dir="rtl">
				<aside class="rest-pos__sidebar">
					<div class="rest-pos__brand">
						<div class="rest-pos__brand-icon">🍽️</div>
						<div class="rest-pos__brand-title">${__("Al-Dhawaqa Restaurant")}</div>
						<div class="rest-pos__brand-sub">AL-DHAWAQA RESTAURANT</div>
					</div>
					<nav class="rest-pos__nav">
						<button class="rest-pos__nav-item is-active" data-nav="orders">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h10"/></svg>
							<span>${__("Orders")}</span>
						</button>
						<button class="rest-pos__nav-item" data-nav="history">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
							<span>${__("Previous Orders")}</span>
						</button>
						<button class="rest-pos__nav-item" data-nav="customers">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
							<span>${__("Customers")}</span>
						</button>
						<button class="rest-pos__nav-item" data-nav="products">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
							<span>${__("Products")}</span>
						</button>
						<button class="rest-pos__nav-item" data-nav="inventory">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
							<span>${__("Inventory")}</span>
						</button>
						<button class="rest-pos__nav-item" data-nav="reports">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M7 16l4-6 4 3 5-8"/></svg>
							<span>${__("Reports")}</span>
						</button>
						<button class="rest-pos__nav-item" data-nav="settings">
							<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
							<span>${__("Settings")}</span>
						</button>
					</nav>
					<button class="rest-pos__logout" id="rest-pos-logout">
						<span>⏻</span><span>${__("Logout")}</span>
					</button>
				</aside>
				<main class="rest-pos__main">
					<div class="rest-pos__topbar">
						<div class="rest-pos__search-wrap">
							<span class="rest-pos__search-icon">🔍</span>
							<input class="rest-pos__search" id="rest-pos-search" placeholder="${__("Search for a product...")}">
						</div>
						<div class="rest-pos__clock-btn" id="rest-pos-clock">🕐</div>
						<div class="rest-pos__notify">🔔<span class="rest-pos__notify-badge">3</span></div>
						<div class="rest-pos__user">
							<div>
								<div class="rest-pos__user-name">${__("Cashier")} ${frappe.utils.escape_html(cashier)}</div>
							</div>
							<div class="rest-pos__avatar">${frappe.utils.escape_html(initial)}</div>
						</div>
					</div>
					<div class="rest-pos__categories" id="rest-pos-categories"></div>
					<div class="rest-pos__grid" id="rest-pos-grid"></div>
				</main>
				<aside class="rest-pos__cart">
					<div class="rest-pos__cart-head">
						<div class="rest-pos__cart-title">${__("Current Order")}</div>
						<div class="rest-pos__cart-meta" id="rest-pos-order-meta">${__("Order No")}: —</div>
					</div>
					<div class="rest-pos__cart-items" id="rest-pos-cart-items"></div>
					<div class="rest-pos__totals" id="rest-pos-totals"></div>
					<div class="rest-pos__actions">
						<button class="rest-pos__clear" id="rest-pos-clear" title="${__("Clear Order")}">🗑️</button>
						<button class="rest-pos__complete" id="rest-pos-complete" disabled>${__("Complete Order")}</button>
					</div>
				</aside>
			</div>
		`);
		$(this.page.body).empty().append($root);
		this.$root = $root;
		this.tick_clock();
	},

	bind_events() {
		const self = this;
		this.$root.on("input", "#rest-pos-search", function () {
			self.state.search = $(this).val() || "";
			self.render_products();
		});
		this.$root.on("click", ".rest-pos__cat", function () {
			self.state.activeCategory = $(this).data("category");
			self.$root.find(".rest-pos__cat").removeClass("is-active");
			$(this).addClass("is-active");
			self.render_products();
		});
		this.$root.on("click", ".rest-pos__card", function () {
			self.add_product($(this).data("item"));
		});
		this.$root.on("click", ".rest-pos__cart-remove", function (e) {
			e.stopPropagation();
			self.remove_line($(this).data("row"));
		});
		this.$root.on("click", "#rest-pos-complete", () => self.complete_order());
		this.$root.on("click", "#rest-pos-clear", () => self.clear_order());
		this.$root.on("click", "#rest-pos-logout", () => frappe.app.logout());
		this.$root.on("click", ".rest-pos__nav-item", function () {
			const nav = $(this).data("nav");
			self.$root.find(".rest-pos__nav-item").removeClass("is-active");
			$(this).addClass("is-active");
			if (nav === "orders") {
				omnexa_restaurant.product_manager.close();
				return;
			}
			if (nav === "products") {
				omnexa_restaurant.product_manager.open();
				return;
			}
			if (nav === "history") {
				frappe.set_route("List", "Restaurant Order");
				return;
			}
			if (nav === "customers") {
				self.open_customer_picker();
				return;
			}
			if (nav === "inventory") {
				omnexa_restaurant.product_manager.state.type = "Raw Material";
				omnexa_restaurant.product_manager.open();
				return;
			}
			if (nav === "reports") {
				frappe.set_route("query-report", "Restaurant Sales Summary");
				return;
			}
			frappe.show_alert({ message: __("Coming soon"), indicator: "blue" });
		});
	},

	tick_clock() {
		const update = () => {
			const now = new Date();
			const hh = String(now.getHours()).padStart(2, "0");
			const mm = String(now.getMinutes()).padStart(2, "0");
			this.$root.find("#rest-pos-clock").text(`${hh}:${mm}`);
		};
		update();
		this._clockTimer = setInterval(update, 30000);
	},

	bootstrap() {
		frappe.call({
			method: "omnexa_restaurant.api.get_pos_catalog",
			callback: (r) => {
				this.state.catalog = r.message || { categories: [], items_by_category: {} };
				this.render_categories();
				this.render_products();
				this.ensure_order();
			},
		});
	},

	ensure_order() {
		frappe.call({
			method: "omnexa_restaurant.api.get_open_pos_orders",
			callback: (r) => {
				const orders = r.message || [];
				if (orders.length) {
					this.state.currentOrder = orders[0].name;
					this.load_order();
					return;
				}
				frappe.call({
					method: "omnexa_restaurant.api.create_pos_order",
					args: { order_type: "Dine-in" },
					callback: (res) => {
						this.state.currentOrder = res.message.order_name;
						this.load_order();
					},
				});
			},
		});
	},

	load_order() {
		if (!this.state.currentOrder) return;
		frappe.call({
			method: "omnexa_restaurant.api.get_pos_order_detail",
			args: { order_name: this.state.currentOrder },
			callback: (r) => {
				this.state.orderDetail = r.message || null;
				this.render_cart();
			},
		});
	},

	category_label(cat) {
		return this.CATEGORY_AR[cat] || cat;
	},

	render_categories() {
		const cats = this.state.catalog.categories || [];
		const allLabel = __("All");
		const buttons = [`<button class="rest-pos__cat is-active" data-category="${allLabel}">${allLabel}</button>`]
			.concat(
				cats.map(
					(cat) =>
						`<button class="rest-pos__cat" data-category="${frappe.utils.escape_html(cat)}">${frappe.utils.escape_html(
							this.category_label(cat)
						)}</button>`
				)
			)
			.join("");
		this.$root.find("#rest-pos-categories").html(buttons);
		this.state.activeCategory = allLabel;
	},

	item_gradient(name, idx) {
		const hash = (name || "").split("").reduce((a, c) => a + c.charCodeAt(0), 0);
		return this.FOOD_GRADIENTS[(hash + idx) % this.FOOD_GRADIENTS.length];
	},

	filtered_items() {
		const map = this.state.catalog.items_by_category || {};
		const all = Object.values(map).flat();
		const search = (this.state.search || "").trim().toLowerCase();
		let items = all;
		if (this.state.activeCategory && this.state.activeCategory !== __("All")) {
			items = map[this.state.activeCategory] || [];
		}
		if (search) {
			items = items.filter((i) => (i.item_name || "").toLowerCase().includes(search) || (i.name || "").toLowerCase().includes(search));
		}
		return items;
	},

	render_products() {
		const items = this.filtered_items();
		if (!items.length) {
			this.$root.find("#rest-pos-grid").html(`<div class="rest-pos__empty">${__("No menu items found.")}</div>`);
			return;
		}
		const html = items
			.map((item, idx) => {
				const price = format_currency(item.effective_price || item.default_price || 0, frappe.defaults.get_default("currency"), 2);
				const bg = item.image ? `url('${item.image}')` : this.item_gradient(item.item_name, idx);
				const bgStyle = item.image ? `background-image:${bg}` : `background-image:${bg}`;
				const offerTag = item.has_offer ? `<span class="rest-pos__offer-tag">${__("Offer")}</span>` : "";
				return `
					<div class="rest-pos__card" data-item="${frappe.utils.escape_html(item.name)}">
						<div class="rest-pos__card-img" style="${bgStyle}">${offerTag}</div>
						<div class="rest-pos__card-body">
							<div class="rest-pos__card-name">${frappe.utils.escape_html(item.item_name)}</div>
							<div class="rest-pos__card-price">${price}</div>
						</div>
					</div>`;
			})
			.join("");
		this.$root.find("#rest-pos-grid").html(html);
	},

	render_cart() {
		const detail = this.state.orderDetail;
		if (!detail) {
			this.$root.find("#rest-pos-cart-items").html(`<div class="rest-pos__cart-empty">${__("Cart is empty")}</div>`);
			this.$root.find("#rest-pos-totals").empty();
			this.$root.find("#rest-pos-order-meta").text(`${__("Order No")}: —`);
			this.$root.find("#rest-pos-complete").prop("disabled", true);
			return;
		}
		this.$root
			.find("#rest-pos-order-meta")
			.text(`${__("Order No")}: #${detail.display_number} · ${detail.items_count || 0} ${__("items")}`);
		if (!detail.items || !detail.items.length) {
			this.$root.find("#rest-pos-cart-items").html(`<div class="rest-pos__cart-empty">${__("Cart is empty")}</div>`);
		} else {
			const rows = detail.items
				.map(
					(row) => `
				<div class="rest-pos__cart-row">
					<div class="rest-pos__cart-row-name">${frappe.utils.escape_html(row.item_name)}</div>
					<div class="rest-pos__cart-row-qty">${row.quantity}</div>
					<div class="rest-pos__cart-row-price">${format_currency(row.line_amount)}</div>
					<button class="rest-pos__cart-remove" data-row="${row.row_name}">×</button>
				</div>`
				)
				.join("");
			this.$root.find("#rest-pos-cart-items").html(rows);
		}
		this.$root.find("#rest-pos-totals").html(`
			<div class="rest-pos__total-row"><span>${__("Subtotal")}</span><span>${format_currency(detail.subtotal)}</span></div>
			<div class="rest-pos__total-row"><span>${__("VAT (15%)")}</span><span>${format_currency(detail.vat)}</span></div>
			<div class="rest-pos__total-row rest-pos__total-row--grand"><span>${__("Total")}</span><span>${format_currency(detail.grand_total)}</span></div>
		`);
		this.$root.find("#rest-pos-complete").prop("disabled", !(detail.items && detail.items.length));
	},

	add_product(menu_item) {
		if (!this.state.currentOrder) return;
		frappe.call({
			method: "omnexa_restaurant.api.add_item_to_order",
			args: { order_name: this.state.currentOrder, menu_item, qty: 1 },
			callback: () => this.load_order(),
		});
	},

	remove_line(row_name) {
		if (!this.state.currentOrder) return;
		frappe.call({
			method: "omnexa_restaurant.api.remove_item_from_order",
			args: { order_name: this.state.currentOrder, row_name },
			callback: (r) => {
				this.state.orderDetail = r.message;
				this.render_cart();
			},
		});
	},

	clear_order() {
		const detail = this.state.orderDetail;
		if (!detail || !detail.items || !detail.items.length) return;
		const rows = [...detail.items];
		const remove_next = () => {
			const row = rows.pop();
			if (!row) {
				this.load_order();
				return;
			}
			frappe.call({
				method: "omnexa_restaurant.api.remove_item_from_order",
				args: { order_name: this.state.currentOrder, row_name: row.row_name },
				callback: () => remove_next(),
			});
		};
		remove_next();
	},

	complete_order() {
		if (!this.state.currentOrder) return;
		const self = this;
		frappe.call({
			method: "omnexa_restaurant.api.complete_pos_order",
			args: { order_name: this.state.currentOrder, customer: this.state.customer || null },
			freeze: true,
			callback: (r) => {
				const html = (r.message && r.message.receipt_html) || "";
				const si = (r.message && r.message.sales_invoice) || "";
				this.print_receipt(html);
				let msg = __("Order completed");
				if (si) msg += ` · ${si}`;
				frappe.show_alert({ message: msg, indicator: "green" });
				this.state.currentOrder = null;
				this.state.orderDetail = null;
				this.state.customer = null;
				frappe.call({
					method: "omnexa_restaurant.api.create_pos_order",
					args: { order_type: "Dine-in" },
					callback: (res) => {
						self.state.currentOrder = res.message.order_name;
						self.load_order();
					},
				});
			},
		});
	},

	open_customer_picker() {
		const self = this;
		frappe.prompt(
			[{ fieldname: "customer", label: __("Customer"), fieldtype: "Link", options: "Customer" }],
			(values) => {
				self.state.customer = values.customer;
				frappe.show_alert({ message: __("Customer selected"), indicator: "blue" });
			},
			__("Select Customer")
		);
	},

	print_receipt(html) {
		if (!html) return;
		const win = window.open("", "_blank", "width=320,height=720");
		if (!win) {
			frappe.msgprint(__("Allow pop-ups to print the receipt."));
			return;
		}
		win.document.write(html);
		win.document.close();
		win.focus();
		setTimeout(() => {
			win.print();
		}, 400);
	},
};
