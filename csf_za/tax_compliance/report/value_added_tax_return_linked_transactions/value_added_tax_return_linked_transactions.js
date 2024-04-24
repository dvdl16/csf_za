// Copyright (c) 2024, Dirk van der Laarse and contributors
// For license information, please see license.txt

frappe.query_reports["Value-added Tax Return Linked Transactions"] = {
	"filters": [
		{
			"fieldname": "vat_return",
			"label": __("Value-added Tax Return"),
			"fieldtype": "Link",
			"options": "Value-added Tax Return",
			"reqd": 1
		},
		{
			"fieldname": "classification",
			"label": __("Classification"),
			"fieldtype": "Select",
			"options": "Output - A Standard rate (excl capital goods)\nOutput - B Standard rate (only capital goods)\nOutput - C Zero Rated (excl goods exported)\nOutput - D Zero Rated (only goods exported)\nOutput - E Exempt\nInput - A Capital goods and/or services supplied to you (local)\nInput - B Capital goods imported\nInput - C Other goods supplied to you (excl capital goods)\nInput - D Other goods imported (excl capital goods)",
		},
		{
			"fieldname": "show_all_classifications",
			"label": __("Show all Classifications"),
			"fieldtype": "Check",
			on_change: function() {
				frappe.query_report.set_filter_value('classification', "");
			}
		},
	],
};
