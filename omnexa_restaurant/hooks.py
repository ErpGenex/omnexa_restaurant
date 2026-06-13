app_name = "omnexa_restaurant"
app_title = "ErpGenEx Restaurant"
app_publisher = "ErpGenEx"
app_description = "Global Restaurant and Cafe Management"
app_email = "dev@erpgenex.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["omnexa_accounting", "omnexa_customer_core"]

# Each item in the list will be shown as an app in the apps page
add_to_apps_screen = [
	{
		"name": "omnexa_restaurant",
		"logo": "/assets/omnexa_restaurant/restaurant.svg",
		"title": "Restaurant",
		"route": "/app/restaurant",
	}
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/omnexa_restaurant/css/omnexa_restaurant.css"
# app_include_js = "/assets/omnexa_restaurant/js/omnexa_restaurant.js"

# include js, css files in header of web template
# web_include_css = "/assets/omnexa_restaurant/css/omnexa_restaurant.css"
# web_include_js = "/assets/omnexa_restaurant/js/omnexa_restaurant.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "omnexa_restaurant/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "omnexa_restaurant/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "omnexa_restaurant.utils.jinja_methods",
# 	"filters": "omnexa_restaurant.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "omnexa_restaurant.install.before_install"
# after_install = "omnexa_restaurant.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "omnexa_restaurant.uninstall.before_uninstall"
# after_uninstall = "omnexa_restaurant.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "omnexa_restaurant.utils.before_app_install"
# after_app_install = "omnexa_restaurant.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "omnexa_restaurant.utils.before_app_uninstall"
# after_app_uninstall = "omnexa_restaurant.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "omnexa_restaurant.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Restaurant Floor": "omnexa_restaurant.permissions.restaurant_floor_query_conditions",
	"Restaurant Table": "omnexa_restaurant.permissions.restaurant_table_query_conditions",
	"Kitchen Station": "omnexa_restaurant.permissions.kitchen_station_query_conditions",
	"Kitchen Printer": "omnexa_restaurant.permissions.kitchen_printer_query_conditions",
	"Menu Item": "omnexa_restaurant.permissions.menu_item_query_conditions",
	"Menu Category": "omnexa_restaurant.permissions.menu_category_query_conditions",
	"Restaurant Offer": "omnexa_restaurant.permissions.restaurant_offer_query_conditions",
	"Restaurant Recipe": "omnexa_restaurant.permissions.restaurant_recipe_query_conditions",
	"Restaurant Order": "omnexa_restaurant.permissions.restaurant_order_query_conditions",
	"Delivery Zone": "omnexa_restaurant.permissions.delivery_zone_query_conditions",
	"Waste Log": "omnexa_restaurant.permissions.waste_log_query_conditions",
	"Delivery Driver": "omnexa_restaurant.permissions.delivery_driver_query_conditions",
	"Kitchen Ticket": "omnexa_restaurant.permissions.kitchen_ticket_query_conditions",
	"Kitchen Print Template": "omnexa_restaurant.permissions.kitchen_print_template_query_conditions",
	"Kitchen Print Job": "omnexa_restaurant.permissions.kitchen_print_job_query_conditions",
}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Restaurant Floor": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Restaurant Table": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Kitchen Station": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Kitchen Printer": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Menu Item": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Menu Category": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Restaurant Offer": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Restaurant Recipe": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Restaurant Order": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Delivery Zone": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Waste Log": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Delivery Driver": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Kitchen Ticket": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Kitchen Print Template": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
	"Kitchen Print Job": {
		"before_validate": "omnexa_restaurant.permissions.populate_company_branch_from_user_context",
		"validate": "omnexa_restaurant.permissions.enforce_branch_access_for_doc",
	},
}

doctype_js = {"Restaurant Order": "public/js/restaurant_order.js"}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"omnexa_restaurant.tasks.all"
# 	],
# 	"daily": [
# 		"omnexa_restaurant.tasks.daily"
# 	],
# 	"hourly": [
# 		"omnexa_restaurant.tasks.hourly"
# 	],
# 	"weekly": [
# 		"omnexa_restaurant.tasks.weekly"
# 	],
# 	"monthly": [
# 		"omnexa_restaurant.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "omnexa_restaurant.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "omnexa_restaurant.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "omnexa_restaurant.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["omnexa_restaurant.utils.before_request"]
# after_request = ["omnexa_restaurant.utils.after_request"]

# Job Events
# ----------
# before_job = ["omnexa_restaurant.utils.before_job"]
# after_job = ["omnexa_restaurant.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"omnexa_restaurant.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

