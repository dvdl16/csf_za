# Copyright (c) 2024, Dirk van der Laarse and Contributors
# See license.txt

from unittest.mock import MagicMock, patch

import frappe
from frappe.tests.utils import FrappeTestCase


class TestValueaddedTaxReturn(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()  # important to call super() methods when extending TestCase.

	def test_refresh_output_tax_fields(self):
		# Setup the mock object and its returns for gl_entries
		mock_gl_entries = [
			MagicMock(
				incl_tax_amount=100,
				tax_amount=10,
				classification="Output - A Standard rate (excl capital goods)",
			),
			MagicMock(
				incl_tax_amount=200,
				tax_amount=20,
				classification="Output - B Standard rate (only capital goods)",
			),
			MagicMock(
				incl_tax_amount=300,
				tax_amount=30,
				classification="Output - C Zero Rated (excl goods exported)",
			),
			MagicMock(
				incl_tax_amount=400,
				tax_amount=40,
				classification="Output - D Zero Rated (only goods exported)",
			),
			MagicMock(incl_tax_amount=500, tax_amount=50, classification="Output - E Exempt"),
		]

		# Setup the object under test
		vat_return = frappe.new_doc("Value-added Tax Return")
		vat_return.gl_entries = mock_gl_entries
		vat_return.acc_exceed_28_days = 50
		vat_return.acc_exceed_28_days_percent = 10
		vat_return.acc_not_exceed_28_days = 60
		vat_return.TAX_RATE = 5

		# Call the function under test
		vat_return.refresh_output_tax_fields()

		# Verify calculations for each field
		self.assertEqual(vat_return.standard_rate_main_excl, 100)
		self.assertEqual(vat_return.standard_rate_main_incl, 10)
		self.assertEqual(vat_return.standard_rate_capital_excl, 200)
		self.assertEqual(vat_return.stardard_rate_total, 20)
		self.assertEqual(vat_return.zero_rate_main_excl, 300)
		self.assertEqual(vat_return.zero_rate_exported_excl, 400)
		self.assertEqual(vat_return.exempt_excl, 500)
		self.assertEqual(vat_return.acc_exceed_28_days_total, 5)  # 50 * 10% = 5
		self.assertEqual(vat_return.acc_total_excl, 65)  # 5 + 60
		self.assertEqual(vat_return.acc_total_incl, 65 * 0.05)
		self.assertEqual(vat_return.adj_change_in_use_incl, vat_return.adj_change_in_use_excl * 5 / 105)

	def test_refresh_input_tax_fields(self):
		mock_gl_entries = [
			MagicMock(
				tax_amount=100,
				classification="Input - A Capital goods and/or services supplied to you (local)",
			),
			MagicMock(tax_amount=200, classification="Input - B Capital goods imported"),
			MagicMock(
				tax_amount=300, classification="Input - C Other goods supplied to you (excl capital goods)"
			),
			MagicMock(tax_amount=400, classification="Input - D Other goods imported (excl capital goods)"),
		]

		# Setup the object under test
		vat_return = frappe.new_doc("Value-added Tax Return")
		vat_return.gl_entries = mock_gl_entries
		vat_return.total_output_tax = 2000
		vat_return.change_in_use = 50
		vat_return.bad_debts = 20
		vat_return.other = 30

		# Call the function under test
		vat_return.refresh_input_tax_fields()

		# Verify calculations for each field
		self.assertEqual(vat_return.capital_goods_supplied, 100)
		self.assertEqual(vat_return.capital_goods_imported, 200)
		self.assertEqual(vat_return.other_goods_supplied, 300)
		self.assertEqual(vat_return.other_goods_imported, 400)
		self.assertEqual(vat_return.total_input_tax, 1100)  # 100+200+300+400+50+20+30
		self.assertEqual(vat_return.total_vat_payable_refundable, 900)  # 2000 - 1100

	@patch(
		"csf_za.tax_compliance.doctype.value_added_tax_return.value_added_tax_return.frappe.get_cached_doc"
	)
	@patch(
		"csf_za.tax_compliance.doctype.value_added_tax_return.value_added_tax_return.transform_gl_entries"
	)
	@patch(
		"csf_za.tax_compliance.doctype.value_added_tax_return.value_added_tax_return.frappe.get_cached_value"
	)
	@patch(
		"csf_za.tax_compliance.doctype.value_added_tax_return.value_added_tax_return.VAT_RETURN_SETTING_FIELD_MAP",
		[
			{
				"field_name": "vat_field",
				"classification": "Standard VAT",
				"reference_doctype": "Sales Invoice",
			}
		],
	)
	def test_process_gl_entries(self, mock_cached_value, mock_transform, mock_get_cached_doc):
		"""
		Test process_gl_entries function with:
		        - SI-001: Sales Invoice
		        - PI-001: Purchase Invoice with no VAT Template
		        - SI-002: Credit Note
		        - PI-002: Debit Note
		        - JE-001: Journal Entry
		        - JE-002: Journal Entry with negatives
		        - JE-003: Cancelled Journal Entry
		"""
		mock_settings = frappe._dict(
			{"tax_accounts": [frappe._dict({"account": "VAT Account"})], "vat_field": "VAT Template"}
		)
		mock_vouchers = frappe._dict(
			{
				"SI-001": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Sales Invoice",
								"general_ledger_debit": 0,
								"general_ledger_credit": 15,
								"sales_invoice_taxes_total": 115,
								"taxes_and_charges_template": "VAT Template",
							}
						)
					}
				),
				"PI-001": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Purchase Invoice",
								"general_ledger_debit": 15,
								"general_ledger_credit": 0,
								"purchase_invoice_taxes_total": 115,
								"taxes_and_charges_template": None,
							}
						)
					}
				),
				"SI-002": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Sales Invoice",
								"general_ledger_debit": 0,
								"general_ledger_credit": 15,
								"sales_invoice_taxes_total": -115,
								"taxes_and_charges_template": "VAT Template",
							}
						)
					}
				),
				"PI-002": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Purchase Invoice",
								"general_ledger_debit": 15,
								"general_ledger_credit": 0,
								"purchase_invoice_taxes_total": -115,
								"taxes_and_charges_template": "VAT Template",
							}
						)
					}
				),
				"JE-001": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Journal Entry",
								"general_ledger_debit": 15,
								"general_ledger_credit": 0,
							}
						),
						"linked_journal_entries": [
							frappe._dict(
								{
									"journal_entry_account": "VAT Account",
									"journal_entry_account_debit": 15,
									"journal_entry_account_credit": 0,
								}
							),
							frappe._dict(
								{
									"journal_entry_account": "Other Account",
									"journal_entry_account_debit": 100,
									"journal_entry_account_credit": 0,
								}
							),
							frappe._dict(
								{
									"journal_entry_account": "Bank Account",
									"journal_entry_account_debit": 0,
									"journal_entry_account_credit": 115,
								}
							),
						],
					}
				),
				"JE-002": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Journal Entry",
								"general_ledger_debit": -15,
								"general_ledger_credit": 0,
							}
						),
						"linked_journal_entries": [
							frappe._dict(
								{
									"journal_entry_account": "VAT Account",
									"journal_entry_account_debit": -15,
									"journal_entry_account_credit": 0,
								}
							),
							frappe._dict(
								{
									"journal_entry_account": "Other Account",
									"journal_entry_account_debit": -100,
									"journal_entry_account_credit": 0,
								}
							),
							frappe._dict(
								{
									"journal_entry_account": "Bank Account",
									"journal_entry_account_debit": 0,
									"journal_entry_account_credit": -115,
								}
							),
						],
					}
				),
				"JE-003": frappe._dict(
					{
						"voucher": frappe._dict(
							{
								"voucher_type": "Journal Entry",
								"general_ledger_debit": -15,
								"general_ledger_credit": 0,
								"is_cancelled": 1,
							}
						),
						"linked_journal_entries": [],
					}
				),
			}
		)

		mock_get_cached_doc.return_value = mock_settings
		mock_transform.return_value = mock_vouchers
		mock_cached_value.side_effect = lambda doctype, docname, fieldname: "Classified"

		vat_return = frappe.new_doc("Value-added Tax Return")
		results = vat_return.process_gl_entries([])  # input for your GL entries

		self.assertEqual(len(results), 7)

		# Validate different voucher types
		# SI-001: Sales Invoice
		self.assertEqual(results[0].classification, "Standard VAT")
		self.assertEqual(results[0].tax_amount, 15)
		self.assertEqual(results[0].incl_tax_amount, 115)

		# PI-001: Purchase Invoice with no VAT Template
		self.assertEqual(
			results[1].classification, None
		)  # Assuming no classification for missing template
		self.assertEqual(results[1].tax_amount, 15)
		self.assertEqual(results[1].incl_tax_amount, 115)

		# SI-002: Credit Note
		self.assertEqual(results[0].classification, "Standard VAT")
		self.assertEqual(results[2].tax_amount, -15)
		self.assertEqual(results[2].incl_tax_amount, -115)

		# PI-002: Debit Note
		self.assertEqual(results[0].classification, "Standard VAT")
		self.assertEqual(results[3].tax_amount, -15)
		self.assertEqual(results[3].incl_tax_amount, -115)

		# JE-001: Journal Entry
		self.assertEqual(results[4].classification, "Classified")  # Assuming custom classification logic
		self.assertEqual(results[4].tax_amount, 15)
		self.assertEqual(results[4].incl_tax_amount, 115)

		# JE-002: Journal Entry with negatives
		self.assertEqual(results[5].classification, "Classified")  # Assuming custom classification logic
		self.assertEqual(results[5].tax_amount, -15)
		self.assertEqual(results[5].incl_tax_amount, -115)

		# JE-003: Cancelled Journal Entry
		self.assertIsNone(results[6].classification)
		self.assertIsNone(results[6].tax_amount)
		self.assertIsNone(results[6].incl_tax_amount)
