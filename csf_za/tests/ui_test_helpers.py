import frappe
from erpnext import get_default_company
from frappe.tests.ui_test_helpers import whitelist_for_tests
from frappe.utils import add_to_date, now

from csf_za.overrides.accounts.test_bank_statement_import import create_bank_account


@whitelist_for_tests
def setup_data_for_bank_reconciliation_tool_customisation_tests(
	expense_account_name,
	custom_tax_account,
	custom_tax_rate_for_bank_recon,
	custom_cost_center_for_tax_account,
):
	"""
	Prepares data for testing customisations on Bank Reconciliation Tool
	"""
	bank_name = "Test Bank"
	bank_account_name = "_Test Bank"

	# Set up an expense account with defaults
	account = frappe.get_doc("Account", expense_account_name)
	account.custom_tax_account = custom_tax_account
	account.custom_tax_rate_for_bank_recon = custom_tax_rate_for_bank_recon
	account.custom_cost_center_for_tax_account = custom_cost_center_for_tax_account
	account.save()

	# Create a Bank Account
	bank_account = create_bank_account(bank_name=bank_name, account_name=bank_account_name)

	# Create a Bank Transaction for Testing
	frappe.db.truncate("Bank Transaction")
	bank_transaction = frappe.get_doc(
		{
			"doctype": "Bank Transaction",
			"date": add_to_date(now(), days=-7),
			"withdrawal": 100,
			"description": "this is a test bank transaction",
			"bank_account": bank_account.name,
			"status": "Unreconciled",
		}
	).insert()
	bank_transaction.submit()


@whitelist_for_tests
def setup_data_for_payment_entry_customisation_tests(mode_of_payment_name, account_name):
	"""
	Prepares data for testing customisations on Payment Entry
	"""

	# Create new Mode of Payment
	try:
		frappe.get_doc(
			{
				"doctype": "Mode of Payment",
				"mode_of_payment": mode_of_payment_name,
			}
		).insert(ignore_if_duplicate=True)
	except frappe.DuplicateEntryError:
		pass

	# Create a Bank Account
	gl_account = create_gl_account_for_bank(account_name=account_name)

	# Add a default bank account
	mode_of_payment = frappe.get_doc("Mode of Payment", mode_of_payment_name)
	mode_of_payment.accounts = []
	mode_of_payment.append(
		"accounts",
		{"company": gl_account.company, "default_account": gl_account.name},
	)
	mode_of_payment.save()


def create_gl_account_for_bank(account_name):
	try:
		gl_account = frappe.get_doc(
			{
				"doctype": "Account",
				"company": get_default_company(),
				"account_name": account_name,
				"parent_account": "Bank Accounts - SP",
				"type": "Bank",
			}
		).insert(ignore_if_duplicate=True)
	except frappe.DuplicateEntryError:
		pass

	return frappe.get_doc("Account", {"account_name": account_name})
