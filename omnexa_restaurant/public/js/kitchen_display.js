frappe.provide("omnexa_restaurant.kds");

omnexa_restaurant.kds = {
	COLUMNS: [
		{ key: "Pending", title: "جديد", css: "new", next: "Preparing" },
		{ key: "Preparing", title: "قيد التحضير", css: "prep", next: "Ready" },
		{ key: "Ready", title: "جاهز", css: "ready", next: "Delivered" },
		{ key: "Delivered", title: "تم التسليم", css: "done", next: null },
	],

	init(wrapper) {
		this.wrapper = wrapper;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Kitchen Display"),
			single_column: true,
		});
		$(this.page.page_container).addClass("kds-page");
		this.render_shell();
		this.bind_events();
		this.load_board();
		this.tick_clock();
		this._refreshTimer = setInterval(() => this.load_board(true), 30000);
		frappe.realtime.on("restaurant_kds_update", () => this.load_board(true));
	},

	render_shell() {
		const $root = $(`
			<div class="rest-kds" dir="rtl">
				<header class="rest-kds__header">
					<div class="rest-kds__title-wrap">
						<div class="rest-kds__chef-icon">👨‍🍳</div>
						<div class="rest-kds__title">شاشة المطبخ</div>
					</div>
					<div class="rest-kds__header-actions">
						<div class="rest-kds__clock" id="rest-kds-clock">00:00</div>
						<button class="rest-kds__icon-btn" title="${__("Sound")}">🔊</button>
						<button class="rest-kds__icon-btn" title="${__("Settings")}">⚙️</button>
					</div>
				</header>
				<div class="rest-kds__board" id="rest-kds-board"></div>
			</div>
		`);
		$(this.page.body).empty().append($root);
		this.$root = $root;
	},

	bind_events() {
		const self = this;
		this.$root.on("click", ".rest-kds__ticket", function () {
			const ticket = $(this).data("ticket");
			const status = $(this).data("status");
			const col = self.COLUMNS.find((c) => c.key === status);
			if (!col || !col.next) return;
			frappe.call({
				method: "omnexa_restaurant.api.update_kitchen_ticket_status",
				args: { ticket_name: ticket, status: col.next },
				callback: () => self.load_board(true),
			});
		});
	},

	tick_clock() {
		const update = () => {
			const now = new Date();
			const hh = String(now.getHours()).padStart(2, "0");
			const mm = String(now.getMinutes()).padStart(2, "0");
			this.$root.find("#rest-kds-clock").text(`${hh}:${mm}`);
		};
		update();
		this._clockTimer = setInterval(update, 1000);
	},

	load_board(silent) {
		frappe.call({
			method: "omnexa_restaurant.api.get_kds_board",
			freeze: !silent,
			callback: (r) => this.render_board(r.message || {}),
		});
	},

	render_ticket(ticket, column) {
		const items = (ticket.items || [])
			.map((i) => `<li>${i.quantity}x ${frappe.utils.escape_html(i.name)}</li>`)
			.join("");
		const timerClass = `rest-kds__timer--${column.css}`;
		const foot =
			column.key === "Delivered"
				? `<div class="rest-kds__delivered-badge">تم التسليم ✓</div>`
				: `<div class="rest-kds__timer ${timerClass}">${ticket.elapsed_mmss}</div>`;
		return `
			<div class="rest-kds__ticket rest-kds__ticket--${column.css}"
				data-ticket="${frappe.utils.escape_html(ticket.name)}"
				data-status="${column.key}">
				<div class="rest-kds__ticket-top">
					<div class="rest-kds__ticket-no">#${frappe.utils.escape_html(ticket.order_number)}</div>
					<div class="rest-kds__ticket-time">${ticket.time_label || ""}</div>
				</div>
				<ul class="rest-kds__ticket-items">${items}</ul>
				<div class="rest-kds__ticket-foot">
					<div>الكاشير: ${frappe.utils.escape_html(ticket.cashier || "")}</div>
					${foot}
				</div>
			</div>`;
	},

	render_board(board) {
		const html = this.COLUMNS.map((column) => {
			const tickets = board[column.key] || [];
			const cards = tickets.length
				? tickets.map((t) => this.render_ticket(t, column)).join("")
				: `<div class="rest-kds__empty">${__("No tickets")}</div>`;
			return `
				<section class="rest-kds__column">
					<div class="rest-kds__column-head rest-kds__column-head--${column.css}">
						<span>${column.title}</span>
						<span>(${tickets.length})</span>
					</div>
					<div class="rest-kds__column-body">${cards}</div>
				</section>`;
		}).join("");
		this.$root.find("#rest-kds-board").html(html);
	},
};
