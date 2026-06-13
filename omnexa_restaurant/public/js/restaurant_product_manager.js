frappe.provide("omnexa_restaurant.product_manager");

omnexa_restaurant.product_manager = {
	TYPES: [
		{ key: "Product", label: __("Products") },
		{ key: "Service", label: __("Services") },
		{ key: "Raw Material", label: __("Raw Materials") },
		{ key: "Bundle", label: __("Bundles") },
		{ key: "Offers", label: __("Offers") },
	],

	init(pos) {
		this.pos = pos;
		this.state = { type: "Product", search: "", items: [], categories: [], offers: [], editing: null };
		this.mount();
		this.bind();
	},

	mount() {
		const html = `
			<div class="rest-prod-panel" id="rest-prod-panel">
				<div class="rest-prod-panel__head">
					<div class="rest-prod-panel__title">${__("Product Management")}</div>
					<button class="btn btn-sm btn-default" id="rest-prod-close">${__("Back to POS")}</button>
				</div>
				<div class="rest-prod-panel__tabs" id="rest-prod-tabs"></div>
				<div class="rest-prod-panel__toolbar">
					<input class="rest-prod-panel__search" id="rest-prod-search" placeholder="${__("Search products...")}">
					<button class="rest-prod-panel__add" id="rest-prod-add">${__("Add New")}</button>
				</div>
				<div class="rest-prod-panel__body" id="rest-prod-body"></div>
			</div>
			<div class="rest-prod-modal-backdrop" id="rest-prod-modal">
				<div class="rest-prod-modal">
					<h4 id="rest-prod-modal-title">${__("Menu Item")}</h4>
					<div class="rest-prod-form-grid" id="rest-prod-form"></div>
					<div class="rest-prod-modal__foot">
						<button class="rest-prod-modal__cancel" id="rest-prod-cancel">${__("Cancel")}</button>
						<button class="rest-prod-modal__save" id="rest-prod-save">${__("Save")}</button>
					</div>
				</div>
			</div>`;
		this.pos.$root.find(".rest-pos__main").append(html);
		this.$panel = this.pos.$root.find("#rest-prod-panel");
		this.$modal = this.pos.$root.find("#rest-prod-modal");
		this.render_tabs();
	},

	bind() {
		const self = this;
		this.pos.$root.on("click", "#rest-prod-close", () => this.close());
		this.pos.$root.on("click", ".rest-prod-tab", function () {
			self.state.type = $(this).data("type");
			self.render_tabs();
			self.load();
		});
		this.pos.$root.on("input", "#rest-prod-search", function () {
			self.state.search = $(this).val() || "";
			self.load();
		});
		this.pos.$root.on("click", "#rest-prod-add", () => self.open_form());
		this.pos.$root.on("click", "#rest-prod-cancel", () => self.$modal.removeClass("is-open"));
		this.pos.$root.on("click", "#rest-prod-save", () => self.save_form());
		this.pos.$root.on("click", ".rest-prod-edit", function () {
			self.open_form($(this).data("name"));
		});
		this.pos.$root.on("click", ".rest-prod-toggle", function () {
			frappe.call({
				method: "omnexa_restaurant.menu_manager.toggle_menu_item_active",
				args: { name: $(this).data("name"), is_active: $(this).data("active") ? 0 : 1 },
				callback: () => self.load(),
			});
		});
		this.pos.$root.on("click", "#rest-prod-upload", () => self.upload_image());
		this.pos.$root.on("click", "#rest-prod-add-ing", () => self.add_ingredient_row());
		this.pos.$root.on("click", "#rest-prod-add-bundle", () => self.add_bundle_row());
	},

	open() {
		this.$panel.addClass("is-open");
		this.load_categories();
		this.load();
	},

	close() {
		this.$panel.removeClass("is-open");
		this.pos.bootstrap();
	},

	render_tabs() {
		const html = this.TYPES.map(
			(t) =>
				`<button class="rest-prod-tab ${this.state.type === t.key ? "is-active" : ""}" data-type="${t.key}">${t.label}</button>`
		).join("");
		this.pos.$root.find("#rest-prod-tabs").html(html);
	},

	load_categories() {
		frappe.call({
			method: "omnexa_restaurant.menu_manager.get_menu_categories",
			callback: (r) => {
				this.state.categories = r.message || [];
			},
		});
	},

	load() {
		if (this.state.type === "Offers") {
			frappe.call({
				method: "omnexa_restaurant.menu_manager.get_restaurant_offers",
				callback: (r) => {
					this.state.offers = r.message || [];
					this.render_offers();
				},
			});
			return;
		}
		frappe.call({
			method: "omnexa_restaurant.menu_manager.get_menu_items_for_manager",
			args: { item_type: this.state.type, search: this.state.search || null },
			callback: (r) => {
				this.state.items = r.message || [];
				this.render_items();
			},
		});
	},

	render_items() {
		const rows = this.state.items
			.map((item) => {
				const img = item.image
					? `<img class="rest-prod-thumb" src="${item.image}" alt="">`
					: `<div class="rest-prod-thumb"></div>`;
				const offer = item.has_offer ? `<span class="rest-prod-badge">${__("Offer")}</span>` : "";
				return `<tr>
					<td>${img}</td>
					<td>${frappe.utils.escape_html(item.item_name)} ${offer}<div class="text-muted small">${frappe.utils.escape_html(item.item_code || "")}</div></td>
					<td>${frappe.utils.escape_html(item.item_type)}</td>
					<td>${frappe.utils.escape_html(item.category || "")}</td>
					<td>${format_currency(item.effective_price || item.default_price)}</td>
					<td class="rest-prod-actions">
						<button class="rest-prod-edit" data-name="${item.name}">✏️</button>
						<button class="rest-prod-toggle" data-name="${item.name}" data-active="${item.is_active ? 1 : 0}">${item.is_active ? "🟢" : "⚪"}</button>
					</td>
				</tr>`;
			})
			.join("");
		this.pos.$root.find("#rest-prod-body").html(`
			<table class="rest-prod-table">
				<thead><tr><th></th><th>${__("Name")}</th><th>${__("Type")}</th><th>${__("Category")}</th><th>${__("Price")}</th><th></th></tr></thead>
				<tbody>${rows || `<tr><td colspan="6" class="text-center text-muted">${__("No items")}</td></tr>`}</tbody>
			</table>`);
	},

	render_offers() {
		const rows = (this.state.offers || [])
			.map(
				(o) => `<tr>
				<td>${frappe.utils.escape_html(o.offer_name)}</td>
				<td>${frappe.utils.escape_html(o.offer_type)}</td>
				<td>${o.menu_item || __("All")}</td>
				<td>${o.offer_type === "Fixed Price" ? format_currency(o.fixed_price) : `${o.discount_percent || 0}%`}</td>
				<td>${o.is_active ? "✅" : "—"}</td>
			</tr>`
			)
			.join("");
		this.pos.$root.find("#rest-prod-body").html(`
			<table class="rest-prod-table">
				<thead><tr><th>${__("Offer")}</th><th>${__("Type")}</th><th>${__("Item")}</th><th>${__("Value")}</th><th>${__("Active")}</th></tr></thead>
				<tbody>${rows || `<tr><td colspan="5" class="text-center text-muted">${__("No offers")}</td></tr>`}</tbody>
			</table>`);
	},

	open_form(name) {
		const isOffer = this.state.type === "Offers" && !name;
		if (isOffer) {
			this.render_offer_form({});
			this.$modal.addClass("is-open");
			return;
		}
		if (!name) {
			this.render_item_form({});
			this.$modal.addClass("is-open");
			return;
		}
		frappe.call({
			method: "omnexa_restaurant.menu_manager.get_menu_item_detail",
			args: { name },
			callback: (r) => {
				this.state.editing = r.message;
				this.render_item_form(r.message || {});
				this.$modal.addClass("is-open");
			},
		});
	},

	render_item_form(data) {
		this.state.editing = data;
		const cats = (this.state.categories || [])
			.map((c) => `<option value="${c.category_name}" ${data.category === c.category_name ? "selected" : ""}>${c.name_ar || c.category_name}</option>`)
			.join("");
		const imgStyle = data.image ? `background-image:url('${data.image}')` : "";
		this.pos.$root.find("#rest-prod-modal-title").text(data.name ? __("Edit Item") : __("New Item"));
		this.pos.$root.find("#rest-prod-form").html(`
			<div class="full"><div class="rest-prod-image-preview" style="${imgStyle}"></div><button type="button" class="btn btn-sm btn-default" id="rest-prod-upload">${__("Upload Image")}</button><input type="hidden" id="f-image" value="${data.image || ""}"></div>
			<div><label>${__("Item Code")}</label><input id="f-code" value="${frappe.utils.escape_html(data.item_code || "")}"></div>
			<div><label>${__("Item Name")}</label><input id="f-name" value="${frappe.utils.escape_html(data.item_name || "")}"></div>
			<div><label>${__("Type")}</label><select id="f-type">
				<option value="Product" ${data.item_type === "Product" ? "selected" : ""}>${__("Product")}</option>
				<option value="Service" ${data.item_type === "Service" ? "selected" : ""}>${__("Service")}</option>
				<option value="Raw Material" ${data.item_type === "Raw Material" ? "selected" : ""}>${__("Raw Material")}</option>
				<option value="Bundle" ${data.item_type === "Bundle" ? "selected" : ""}>${__("Bundle")}</option>
			</select></div>
			<div><label>${__("Category")}</label><select id="f-category"><option value=""></option>${cats}</select></div>
			<div><label>${__("Price")}</label><input type="number" step="0.01" id="f-price" value="${data.default_price || 0}"></div>
			<div><label>${__("Tax Code")}</label><input id="f-tax" value="${frappe.utils.escape_html(data.classification_code || "")}"></div>
			<div class="full"><label>${__("Description")}</label><textarea id="f-desc" rows="2">${frappe.utils.escape_html(data.description || "")}</textarea></div>
			<div class="full" id="f-ingredients-wrap"><label>${__("Recipe Ingredients (ErpGenex Items)")}</label><div id="f-ingredients"></div><button type="button" class="btn btn-xs btn-default" id="rest-prod-add-ing">+ ${__("Ingredient")}</button></div>
			<div class="full" id="f-bundle-wrap" style="display:none;"><label>${__("Bundle Components")}</label><div id="f-bundle"></div><button type="button" class="btn btn-xs btn-default" id="rest-prod-add-bundle">+ ${__("Component")}</button></div>
		`);
		this.render_ingredient_rows(data.ingredients || []);
		this.render_bundle_rows(data.bundle_items || []);
		this.pos.$root.find("#f-type").on("change", function () {
			const t = $(this).val();
			$("#f-bundle-wrap").toggle(t === "Bundle");
			$("#f-ingredients-wrap").toggle(t !== "Service");
		}).trigger("change");
	},

	render_offer_form(data) {
		this.state.editing = { _offer: true, ...data };
		this.pos.$root.find("#rest-prod-modal-title").text(__("New Offer"));
		this.pos.$root.find("#rest-prod-form").html(`
			<div class="full"><label>${__("Offer Name")}</label><input id="o-name"></div>
			<div><label>${__("Type")}</label><select id="o-type"><option value="Percent Discount">${__("Percent Discount")}</option><option value="Fixed Price">${__("Fixed Price")}</option></select></div>
			<div><label>${__("Menu Item")} (${__("optional")})</label><input id="o-item" placeholder="${__("Leave blank for all")}"></div>
			<div><label>${__("Discount %")}</label><input type="number" id="o-disc" value="0"></div>
			<div><label>${__("Fixed Price")}</label><input type="number" id="o-fixed" value="0"></div>
		`);
	},

	render_ingredient_rows(rows) {
		const html = (rows || [])
			.map(
				(r, i) => `<div class="rest-prod-ing-row" data-i="${i}">
				<input class="ing-item" value="${frappe.utils.escape_html(r.ingredient_item || "")}" placeholder="${__("ErpGenex Item")}">
				<input class="ing-qty" type="number" step="0.01" value="${r.qty || 1}">
				<input class="ing-waste" type="number" step="0.1" value="${r.waste_percentage || 0}" placeholder="%">
				<button type="button" class="btn btn-xs btn-danger ing-del">×</button>
			</div>`
			)
			.join("");
		this.pos.$root.find("#f-ingredients").html(html);
		this.pos.$root.find(".ing-del").on("click", function () {
			$(this).closest(".rest-prod-ing-row").remove();
		});
	},

	render_bundle_rows(rows) {
		const html = (rows || [])
			.map(
				(r) => `<div class="rest-prod-bundle-row">
				<input class="b-item" value="${frappe.utils.escape_html(r.menu_item || "")}" placeholder="${__("Menu Item")}">
				<input class="b-qty" type="number" step="0.01" value="${r.quantity || 1}">
				<span></span><button type="button" class="btn btn-xs btn-danger b-del">×</button>
			</div>`
			)
			.join("");
		this.pos.$root.find("#f-bundle").html(html);
		this.pos.$root.find(".b-del").on("click", function () {
			$(this).closest(".rest-prod-bundle-row").remove();
		});
	},

	add_ingredient_row() {
		this.pos.$root.find("#f-ingredients").append(`<div class="rest-prod-ing-row">
			<input class="ing-item" placeholder="${__("ErpGenex Item")}"><input class="ing-qty" type="number" value="1"><input class="ing-waste" type="number" value="0"><button type="button" class="btn btn-xs btn-danger ing-del">×</button></div>`);
	},

	add_bundle_row() {
		this.pos.$root.find("#f-bundle").append(`<div class="rest-prod-bundle-row">
			<input class="b-item" placeholder="${__("Menu Item")}"><input class="b-qty" type="number" value="1"><span></span><button type="button" class="btn btn-xs btn-danger b-del">×</button></div>`);
	},

	upload_image() {
		new frappe.ui.FileUploader({
			allow_multiple: false,
			restrictions: { allowed_file_types: ["image/*"] },
			on_success: (file) => {
				this.pos.$root.find("#f-image").val(file.file_url);
				this.pos.$root.find(".rest-prod-image-preview").css("background-image", `url('${file.file_url}')`);
			},
		});
	},

	save_form() {
		const data = this.state.editing || {};
		if (data._offer) {
			frappe.call({
				method: "omnexa_restaurant.menu_manager.save_restaurant_offer",
				args: {
					payload_json: JSON.stringify({
						offer_name: this.pos.$root.find("#o-name").val(),
						offer_type: this.pos.$root.find("#o-type").val(),
						menu_item: this.pos.$root.find("#o-item").val() || null,
						discount_percent: this.pos.$root.find("#o-disc").val(),
						fixed_price: this.pos.$root.find("#o-fixed").val(),
						is_active: 1,
					}),
				},
				callback: () => {
					this.$modal.removeClass("is-open");
					this.load();
				},
			});
			return;
		}
		const ingredients = [];
		this.pos.$root.find(".rest-prod-ing-row").each(function () {
			const item = $(this).find(".ing-item").val();
			if (!item) return;
			ingredients.push({
				ingredient_item: item,
				qty: $(this).find(".ing-qty").val(),
				waste_percentage: $(this).find(".ing-waste").val(),
			});
		});
		const bundle_items = [];
		this.pos.$root.find(".rest-prod-bundle-row").each(function () {
			const item = $(this).find(".b-item").val();
			if (!item) return;
			bundle_items.push({ menu_item: item, quantity: $(this).find(".b-qty").val() });
		});
		frappe.call({
			method: "omnexa_restaurant.menu_manager.save_menu_item",
			args: {
				payload_json: JSON.stringify({
					name: data.name,
					item_code: this.pos.$root.find("#f-code").val(),
					item_name: this.pos.$root.find("#f-name").val(),
					item_type: this.pos.$root.find("#f-type").val(),
					category: this.pos.$root.find("#f-category").val(),
					default_price: this.pos.$root.find("#f-price").val(),
					classification_code: this.pos.$root.find("#f-tax").val(),
					description: this.pos.$root.find("#f-desc").val(),
					image: this.pos.$root.find("#f-image").val(),
					is_active: 1,
					ingredients,
					bundle_items,
				}),
			},
			callback: () => {
				this.$modal.removeClass("is-open");
				this.load();
				frappe.show_alert({ message: __("Saved"), indicator: "green" });
			},
		});
	},
};
