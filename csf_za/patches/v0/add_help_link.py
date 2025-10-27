import frappe


def execute():
	"""
	Adds help docs link to Help dropdown
	"""
	navbar_settings = frappe.get_single("Navbar Settings")
	navbar_settings.append(
		"help_dropdown",
		{
			"item_label": "South Africa Customisations Documentation",
			"item_type": "Route",
			"route": "/csf_za_introduction",
			"is_standard": 1,
		},
	)
	navbar_settings.save()
