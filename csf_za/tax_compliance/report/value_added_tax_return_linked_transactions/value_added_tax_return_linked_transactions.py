# Copyright (c) 2024, Dirk van der Laarse and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from pypika import Criterion


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"fieldname": "name",
			"label": _("VAT Return"),
			"fieldtype": "Link",
			"options": "Value-added Tax Return",
			"width": 300,
		},
		{
			"fieldname": "gl_entry",
			"label": _("GL Entry"),
			"fieldtype": "Link",
			"options": "GL Entry",
			"width": 200,
		},
		{
			"fieldname": "voucher_type",
			"label": _("Voucher Type"),
			"width": 150,
		},
		{
			"fieldname": "voucher_no",
			"label": _("Voucher No"),
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 200,
		},
		{
			"fieldname": "posting_date",
			"label": _("Posting Date"),
			"fieldtype": "Date",
			"width": 200,
		},
		{
			"fieldname": "taxes_and_charges",
			"label": _("Taxes and Charges Template"),
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"fieldname": "tax_account_debit",
			"label": _("Tax Account Debit"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "tax_account_credit",
			"label": _("Tax Account Credit"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "tax_amount",
			"label": _("Tax Amount"),
			"fieldtype": "Currency",
			"width": 100,
		},
		{
			"fieldname": "incl_tax_amount",
			"label": _("Incl. Tax Amount"),
			"fieldtype": "Currency",
			"width": 100,
		},
	]
	return columns


def get_data(filters):
	vat_return = filters.get("vat_return")
	classification = filters.get("classification")
	show_all_classifications = filters.get("show_all_classifications")

	vtr = frappe.qb.DocType("Value-added Tax Return")
	vtre = frappe.qb.DocType("Value-added Tax Return GL Entry")

	extra_criterions = []
	if classification:
		extra_criterions.append(vtre.classification == classification)

	# Construct the query using Frappe query builder
	query = (
		frappe.qb.from_(vtr)
		.join(vtre)
		.on(vtre.parent == vtr.name)
		.select(
			vtr.name,
			vtre.gl_entry,
			vtre.voucher_type,
			vtre.voucher_no,
			vtre.posting_date,
			vtre.taxes_and_charges,
			vtre.tax_account_debit,
			vtre.tax_account_credit,
			vtre.tax_amount,
			vtre.incl_tax_amount,
			vtre.classification,
		)
		.where(vtr.name == vat_return)
		.where(Criterion.any(extra_criterions))
	)

	# Execute the query and fetch the result as a list of dictionaries
	result = query.run(as_dict=True)

	if show_all_classifications:
		return group_by_classification(result)
	else:
		return result


def group_by_classification(data):
	""" """
	meta = frappe.get_meta("Value-added Tax Return GL Entry", cached=False)
	classification_field = next(
		(field for field in meta.fields if field.fieldname == "classification")
	)
	classifications = classification_field.options.split("\n")

	grouped_data = {classification: [] for classification in classifications}
	output_data = []
	for row in data:
		grouped_data[row.classification].append(row)

	for classification in grouped_data.keys():
		output_data.append({"name": classification if classification else "Unclassified"})
		sorted_chunk = sorted(grouped_data[classification], key=lambda x: (x.posting_date, x.voucher_no))
		output_data += sorted_chunk

		# Add subtotal row per classification
		output_data.append(
			{
				"name": "Total",
				"tax_account_debit": sum([row["tax_account_debit"] for row in sorted_chunk]),
				"tax_account_credit": sum([row["tax_account_credit"] for row in sorted_chunk]),
				"tax_amount": sum([row["tax_amount"] for row in sorted_chunk]),
				"incl_tax_amount": sum([row["incl_tax_amount"] for row in sorted_chunk]),
			}
		)
		output_data.append({})

	return output_data
