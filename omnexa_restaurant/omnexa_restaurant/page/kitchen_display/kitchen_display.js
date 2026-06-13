frappe.pages["kitchen-display"].on_page_load = function (wrapper) {
	frappe.require(
		[
			"/assets/omnexa_restaurant/css/kitchen_display.css",
			"/assets/omnexa_restaurant/js/kitchen_display.js",
		],
		function () {
			omnexa_restaurant.kds.init(wrapper);
		}
	);
};
