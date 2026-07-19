frappe.pages["restaurant-pos"].on_page_load = function (wrapper) {
	frappe.require(
		[
			"/assets/omnexa_restaurant/css/restaurant_pos.css",
			"/assets/omnexa_restaurant/css/restaurant_product_manager.css",
			"/assets/omnexa_restaurant/js/restaurant_product_manager.js",
			"/assets/omnexa_restaurant/js/restaurant_pos.js",
		],
		function () {
			omnexa_restaurant.pos.init(wrapper);
		}
	);
};
