# Copyright (c) 2024, Dirk van der Laarse and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

VAT_RETURN_SETTING_FIELD_MAP = [
	{
		"field_name": "standard_rate_non_capital",
		"classification": "Output - A Standard rate (excl capital goods)",
		"reference_doctype": "Sales Invoice",
	},
	{
		"field_name": "standard_rate_capital",
		"classification": "Output - B Standard rate (only capital goods) ",
		"reference_doctype": "Sales Invoice",
	},
	{
		"field_name": "zero_rate_non_exported",
		"classification": "Output - C Zero Rated (excl goods exported) ",
		"reference_doctype": "Sales Invoice",
	},
	{
		"field_name": "zero_rate_exported",
		"classification": "Output - D Zero Rated (only goods exported) ",
		"reference_doctype": "Sales Invoice",
	},
	{
		"field_name": "exempt",
		"classification": "Output - E Exempt",
		"reference_doctype": "Sales Invoice",
	},
	{
		"field_name": "input_capital_local",
		"classification": "Input - A Capital goods and/or services supplied to you (local)",
		"reference_doctype": "Purchase Invoice",
	},
	{
		"field_name": "input_capital_import",
		"classification": "Input - B Capital goods imported",
		"reference_doctype": "Purchase Invoice",
	},
	{
		"field_name": "input_goods_local",
		"classification": "Input - C Other goods supplied to you (excl capital goods)",
		"reference_doctype": "Purchase Invoice",
	},
	{
		"field_name": "input_goods_import",
		"classification": "Input - D Other goods imported (excl capital goods)",
		"reference_doctype": "Purchase Invoice",
	},
]


class ValueaddedTaxReturnSettings(Document):
	pass
