# Copyright (c) 2024, Dirk van der Laarse and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from pypika import Case

from csf_za.tax_compliance.doctype.value_added_tax_return_settings.value_added_tax_return_settings import (
	VAT_RETURN_SETTING_FIELD_MAP,
)


class ValueaddedTaxReturn(Document):

	TAX_RATE = 15

	def validate(self):
		"""
		Called on save
		"""
		self.refresh_output_tax_fields()
		self.refresh_input_tax_fields()

	def refresh_output_tax_fields(self):
		"""
		Recalculate output tax calculated fields
		"""
		# Calculate field 1
		self.standard_rate_main_excl = sum(
			[
				row.incl_tax_amount
				for row in self.gl_entries
				if row.classification == "Output - A Standard rate (excl capital goods)"
			]
		)

		# Calculate field 4
		self.standard_rate_main_incl = sum(
			[
				row.tax_amount
				for row in self.gl_entries
				if row.classification == "Output - A Standard rate (excl capital goods)"
			]
		)

		# Calculate field 1a
		self.standard_rate_capital_excl = sum(
			[
				row.incl_tax_amount
				for row in self.gl_entries
				if row.classification == "Output - B Standard rate (only capital goods)"
			]
		)

		# Calculate field 4a
		self.stardard_rate_total = sum(
			[
				row.tax_amount
				for row in self.gl_entries
				if row.classification == "Output - B Standard rate (only capital goods)"
			]
		)

		# Calculate field 2
		self.zero_rate_main_excl = sum(
			[
				row.incl_tax_amount
				for row in self.gl_entries
				if row.classification == "Output - C Zero Rated (excl goods exported)"
			]
		)

		# Calculate field 2a
		self.zero_rate_exported_excl = sum(
			[
				row.incl_tax_amount
				for row in self.gl_entries
				if row.classification == "Output - D Zero Rated (only goods exported)"
			]
		)

		# Calculate field 3
		self.exempt_excl = sum(
			[row.incl_tax_amount for row in self.gl_entries if row.classification == "Output - E Exempt"]
		)

		# Calculate field 6
		self.acc_exceed_28_days_total = (
			self.acc_exceed_28_days * float(self.acc_exceed_28_days_percent) / 100
		)

		# Calculate field 8
		self.acc_total_excl = self.acc_exceed_28_days_total + self.acc_not_exceed_28_days

		# Calculate field 9
		self.acc_total_incl = self.acc_total_excl * self.TAX_RATE / 100

		# Calculate field 11
		self.adj_change_in_use_incl = self.adj_change_in_use_excl * self.TAX_RATE / (100 + self.TAX_RATE)

		# Calculate total output tax
		self.total_output_tax = (
			self.standard_rate_main_incl
			+ self.stardard_rate_total
			+ self.acc_total_incl
			+ self.adj_change_in_use_incl
			+ self.adj_other_incl
		)

	def refresh_input_tax_fields(self):
		"""
		Recalculate input tax calculated fields
		"""
		# Calculate field 14
		self.capital_goods_supplied = sum(
			[
				row.tax_amount
				for row in self.gl_entries
				if row.classification == "Input - A Capital goods and/or services supplied to you (local)"
			]
		)

		# Calculate field 14a
		self.capital_goods_imported = sum(
			[
				row.tax_amount
				for row in self.gl_entries
				if row.classification == "Input - B Capital goods imported"
			]
		)

		# Calculate field 15
		self.other_goods_supplied = sum(
			[
				row.tax_amount
				for row in self.gl_entries
				if row.classification == "Input - C Other goods supplied to you (excl capital goods)"
			]
		)

		# Calculate field 15a
		self.other_goods_imported = sum(
			[
				row.tax_amount
				for row in self.gl_entries
				if row.classification == "Input - D Other goods imported (excl capital goods)"
			]
		)

		# Calculate total input tax
		self.total_input_tax = (
			self.capital_goods_supplied
			+ self.capital_goods_imported
			+ self.other_goods_supplied
			+ self.other_goods_imported
			+ self.change_in_use
			+ self.bad_debts
			+ self.other
		)

		# Calculate final amount
		self.total_vat_payable_refundable = self.total_output_tax - self.total_input_tax

	def on_submit(self):
		"""
		Validate when document is submitted
		"""
		unclassified = [
			row for row in self.gl_entries if not row.classification and not row.is_cancelled
		]
		if len(unclassified) > 0:
			frappe.throw(
				_("Please classify the {0} remaining unclassified transactions before submitting").format(
					len(unclassified)
				)
			)

	@frappe.whitelist()
	def get_gl_entries(self):
		"""
		Retrieve journal entries for linked accounts
		"""
		vat_return_settings = frappe.get_cached_doc("Value-added Tax Return Settings", self.company)

		# Construct the query using Frappe query builder
		gle = frappe.qb.DocType("GL Entry")
		je = frappe.qb.DocType("Journal Entry")
		jea = frappe.qb.DocType("Journal Entry Account")
		si = frappe.qb.DocType("Sales Invoice")
		sitc = frappe.qb.DocType("Sales Taxes and Charges")
		pi = frappe.qb.DocType("Purchase Invoice")
		pitc = frappe.qb.DocType("Purchase Taxes and Charges")

		tax_accounts = [row.account for row in vat_return_settings.tax_accounts]

		query = (
			frappe.qb.from_(gle)
			.left_join(je)
			.on(je.name == gle.voucher_no)
			.left_join(jea)
			.on(jea.parent == je.name)
			.left_join(si)
			.on((gle.voucher_type == "Sales Invoice") & (si.name == gle.voucher_no))
			.left_join(sitc)
			.on(sitc.parent == si.name)
			.left_join(pi)
			.on((gle.voucher_type == "Purchase Invoice") & (pi.name == gle.voucher_no))
			.left_join(pitc)
			.on(pitc.parent == pi.name)
			.select(
				gle.name,
				gle.voucher_type,
				gle.voucher_no,
				gle.posting_date,
				gle.is_cancelled,
				gle.debit_in_account_currency.as_("general_ledger_debit"),
				gle.credit_in_account_currency.as_("general_ledger_credit"),
				je.total_debit.as_("journal_entry_total_debit"),
				je.total_credit.as_("journal_entry_total_credit"),
				je.docstatus.as_("journal_entry_docstatus"),
				jea.account.as_("journal_entry_account"),
				jea.debit.as_("journal_entry_account_debit"),
				jea.credit.as_("journal_entry_account_credit"),
				jea.idx.as_("journal_entry_account_idx"),
				sitc.tax_amount.as_("sales_invoice_taxes_tax_amount"),
				sitc.total.as_("sales_invoice_taxes_total"),
				pitc.tax_amount.as_("purchase_invoice_taxes_tax_amount"),
				pitc.total.as_("purchase_invoice_taxes_total"),
				Case()
				.when(gle.voucher_type == "Sales Invoice", si.taxes_and_charges)
				.when(gle.voucher_type == "Purchase Invoice", pi.taxes_and_charges)
				.else_(None)
				.as_("taxes_and_charges_template"),
			)
			.where(
				(gle.posting_date >= self.date_from)
				& (gle.posting_date <= self.date_to)
				& (gle.account.isin(tax_accounts))
			)
		)

		# Execute the query and fetch the result as a list of dictionaries
		result = query.run(as_dict=True)

		return self.process_gl_entries(result)

	def process_gl_entries(self, gl_entries):
		"""
		Perform classification for each journal entry:
		        - If it's linked to a Sales Invoice or Purchase Invoice, get the Taxes and Charges Template
		          and determine the classification based on the maps in Value-add Tax Return Settings
		        - Else, determine the VAT component and infer the classification based on the G/L Account settings
		"""
		vat_return_settings = frappe.get_cached_doc("Value-added Tax Return Settings", self.company)
		tax_accounts = [row.account for row in vat_return_settings.tax_accounts]

		# The field names on 'Value-added Tax Return Settings' correspond to classifications
		# Create a dict of these fields' values and field names
		taxes_and_charges_map = [
			entry for entry in VAT_RETURN_SETTING_FIELD_MAP if vat_return_settings.get(entry["field_name"])
		]

		vouchers = transform_gl_entries(gl_entries)

		for voucher_no, item in vouchers.items():
			voucher = item.voucher

			# Skip Cancelled GL Entries
			if voucher.is_cancelled:
				continue

			voucher.tax_amount = voucher.general_ledger_debit or voucher.general_ledger_credit

			voucher.classification_debugging = "🚀"
			if voucher.voucher_type in ("Sales Invoice", "Purchase Invoice"):
				voucher.incl_tax_amount = (
					voucher.sales_invoice_taxes_total or voucher.purchase_invoice_taxes_total
				)

				# If the voucher_type is a reversal (e.g. Credit and Debit Notes, change the sign of tax_amount)
				if voucher.incl_tax_amount < 0 and voucher.tax_amount > 0:
					voucher.tax_amount = voucher.tax_amount * -1

				voucher.classification_debugging += (
					"\n🚀 voucher_type is a 'Sales Invoice' or 'Purchase Invoice')"
				)
				voucher.classification_debugging += (
					f"\n🚀 taxes_and_charges_template = '{voucher.taxes_and_charges_template}'"
				)
				if voucher.taxes_and_charges_template:
					# Find the corresponding field name for the voucher's Taxes and Charges Template
					settings_field = next(
						(
							field
							for field in taxes_and_charges_map
							if field["reference_doctype"] == voucher.voucher_type
							and vat_return_settings.get(field["field_name"]) == voucher.taxes_and_charges_template
						),
						None,
					)

					voucher.classification_debugging += f"\n🚀 settings_field = {settings_field}"

					# Get the corresponding classification for this field_name
					if settings_field:
						voucher.classification_debugging += (
							f"\n🚀 classification = {settings_field['classification']}"
						)

						voucher.classification = settings_field["classification"]
						continue
				else:
					voucher.classification_debugging += "\n🚀 No Taxes and Charges template on Invoice, or Taxes and Charges template is not set in 'Value-added Return Settings'"

			if voucher.voucher_type == "Journal Entry":
				voucher.classification_debugging += "\n🚀 voucher_type is 'Journal Entry'"
				# Process pairs of Journal Entry Account child records
				# E.g.
				#
				# |   | account          | debit | credit |
				# |---|------------------|-------|--------|
				# | 1 | interest         | 1000  | 0      |
				# | 2 | bank             | 0     | 1000   |
				# | 3 | fees and charges | 100   |        |
				# | 4 | vat              | 15    | 0      |
				# | 5 | bank             | 0     | 115    |
				#
				# Here we want to ignore transactions that has nothing to do with VAT.
				# Thus, rows 1 and 2 should be filtered out.

				filtered_out = []
				for journal_entry in item.linked_journal_entries:
					if journal_entry not in filtered_out:
						if journal_entry.journal_entry_account_debit != 0:
							debit_amount = journal_entry.journal_entry_account_debit
							contra_entry_with_same_amount = next(
								(
									je
									for je in item.linked_journal_entries
									if je.journal_entry_account_credit == debit_amount
								),
								None,
							)
						elif journal_entry.journal_entry_account_credit != 0:
							credit_amount = journal_entry.journal_entry_account_credit
							contra_entry_with_same_amount = next(
								(
									je
									for je in item.linked_journal_entries
									if je.journal_entry_account_debit == credit_amount
								),
								None,
							)
						if contra_entry_with_same_amount:
							filtered_out += [contra_entry_with_same_amount, journal_entry]

				filtered_journal_entries = [
					item for item in item.linked_journal_entries if item not in filtered_out
				]

				# If there are no entries remaining after filtering, assume it is an entry for SARS Payment/Receipt
				if len(filtered_journal_entries) == 0 and len(filtered_out) > 0:
					voucher.classification = "SARS Payment/Receipt"
					continue

				voucher.classification_debugging += (
					f"\n🚀 filtered_out = rows {[je.journal_entry_account_idx for je in filtered_out]}"
				)
				voucher.classification_debugging += f"\n🚀 filtered_journal_entries = rows {[je.journal_entry_account_idx for je in filtered_journal_entries]}"

				# Identify the tax, tax inclusive and tax exclusve components of manual Journal Entries
				tax_leg = next(
					(je for je in filtered_journal_entries if je.journal_entry_account in tax_accounts), None
				)
				incl_tax_leg = None
				excl_tax_leg = None
				try:
					incl_tax_leg = max(
						[je for je in filtered_journal_entries if je != tax_leg],
						key=lambda je: abs(je.journal_entry_account_credit or je.journal_entry_account_debit),
					)
					excl_tax_leg = min(
						[je for je in filtered_journal_entries if je != tax_leg],
						key=lambda je: abs(je.journal_entry_account_credit or je.journal_entry_account_debit),
					)
				except ValueError as e:
					voucher.classification_debugging += f"\n🚀 {e}]'"

				if all([tax_leg, incl_tax_leg, excl_tax_leg]):
					voucher.classification_debugging += f"\n🚀 tax_leg = '{tax_leg.journal_entry_account}': '{tax_leg.journal_entry_account_credit or tax_leg.journal_entry_account_debit}'"
					voucher.classification_debugging += f"\n🚀 incl_tax_leg = '{incl_tax_leg.journal_entry_account}': '{incl_tax_leg.journal_entry_account_credit or incl_tax_leg.journal_entry_account_debit}'"
					voucher.classification_debugging += f"\n🚀 excl_tax_leg = '{excl_tax_leg.journal_entry_account}': '{excl_tax_leg.journal_entry_account_credit or excl_tax_leg.journal_entry_account_debit}'"

					if excl_tax_leg.journal_entry_account_debit != 0:
						voucher.classification = frappe.get_cached_value(
							"Account", excl_tax_leg.journal_entry_account, "custom_vat_return_debit_classification"
						)
						voucher.incl_tax_amount = (
							incl_tax_leg.journal_entry_account_credit or incl_tax_leg.journal_entry_account_debit
						)
						voucher.classification_debugging += f"\n🚀 'Classify Debit entries...' setting for Account '{excl_tax_leg.journal_entry_account}' = '{voucher.classification}'"
						continue
					elif excl_tax_leg.journal_entry_account_credit != 0:
						voucher.classification = frappe.get_cached_value(
							"Account", excl_tax_leg.journal_entry_account, "custom_vat_return_credit_classification"
						)
						voucher.incl_tax_amount = (
							incl_tax_leg.journal_entry_account_credit or incl_tax_leg.journal_entry_account_debit
						)
						voucher.classification_debugging += f"\n🚀 'Classify Credit entries..' for Account '{excl_tax_leg.journal_entry_account}' = '{voucher.classification}'"
						continue

		return [voucher.voucher for voucher in vouchers.values()]


def transform_gl_entries(gl_entries):
	"""
	Transform flat list of entries to a dict with voucher_no as key
	        E.g.

	        [
	                {
	                        "journal_entry_total_credit": 15850,
	                        "journal_entry_total_debit": 15850,
	                        "name": "ACC-GLE-2024-11691",
	                        "posting_date": "2024-03-01",
	                        .
	                        .
	                        .
	                        "voucher_no": "ACC-JV-2024-00835",
	                        "voucher_type": "Journal Entry",
	                }
	        ]

	        becomes

	        [
	                {
	                        "ACC-JV-2024-00835":
	                                {
	                                        "voucher": {
	                                                "journal_entry_total_credit": 15850,
	                                                "journal_entry_total_debit": 15850,
	                                                "name": "ACC-GLE-2024-11691",
	                                                "posting_date": "2024-03-01",
	                                                .
	                                                .
	                                                .
	                                                "voucher_no": "ACC-JV-2024-00835",
	                                                "voucher_type": "Journal Entry",
	                                        }
	                                        "linked_journal_entries": [
	                                                .
	                                                .
	                                                .
	                                        ]
	                                }
	                }
	        ]
	"""
	vouchers = {}
	for entry in gl_entries:
		vouchers.setdefault(entry.name, frappe._dict({"voucher": entry, "linked_journal_entries": []}))[
			"linked_journal_entries"
		].append(entry)

	return vouchers
