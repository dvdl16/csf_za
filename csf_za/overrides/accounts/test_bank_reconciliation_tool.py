# from unittest.mock import MagicMock

# import frappe
# from erpnext import get_default_company, get_default_cost_center
# from frappe.tests.utils import FrappeTestCase
# from frappe.utils.data import now_datetime

# from csf_za.overrides.accounts.bank_reconciliation_tool import custom_create_journal_entry_bts
# from csf_za.overrides.accounts.test_bank_statement_import import create_bank_account

# default_company = get_default_company()
# default_bank = "Test Bank"

# test_bank_transaction = {
# 	"doctype": "Bank Transaction",
# 	"description": "1512567 BG/000002918 OPSKATTUZWXXX AT776000000098709837 Herr G",
# 	"date": f"{now_datetime().year}-04-20",
# 	"deposit": 115,
# 	"currency": "ZAR",
# 	"bank_account": "Checking Account - Test Bank",
# }


# class TestBankReconciliationToolOverrides(FrappeTestCase):
# 	@classmethod
# 	def setUpClass(cls):
# 		super().setUpClass()  # important to call super() methods when extending TestCase.

# 	def setUp(self):
# 		create_bank_account(bank_name=default_bank, account_name="_Test Bank", company=default_company)

# 	def test_custom_create_journal_entry_bts_calculates_vat_correctly_when_rate_is_supplied(self):
# 		"""
# 		Test custom_create_journal_entry_bts creates a correct Journal Entry when custom_tax_account and custom_tax_rate_for_bank_recon are supplied
# 		"""
# 		bank_transaction = make_bank_transaction_test_record()

# 		# Call the custom_create_journal_entry_bts function with test data
# 		custom_create_journal_entry_bts(
# 			bank_transaction_name=bank_transaction.name,
# 			reference_number=test_bank_transaction["description"],
# 			reference_date=test_bank_transaction["date"],
# 			posting_date=test_bank_transaction["date"],
# 			entry_type="Bank Entry",
# 			second_account="Telephone Expenses - SP",
# 			custom_tax_account="VAT - SP",
# 			custom_tax_rate_for_bank_recon=15,
# 		)

# 		# Fetch the created journal entry using the test transaction's description
# 		journal_entry = frappe.get_doc(
# 			"Journal Entry", {"cheque_no": test_bank_transaction["description"]}
# 		)

# 		# Check if the journal entry exists
# 		assert journal_entry

# 		# Check if the first account in the journal entry is "Telephone Expenses - SP", as per the test data
# 		assert journal_entry.accounts[0].account == "Telephone Expenses - SP"

# 		# Check if the credit amount for the first account is the total amount minus VAT
# 		assert journal_entry.accounts[0].credit_in_account_currency == 100

# 		# Check if the second account in the journal entry is "VAT - SP"
# 		assert journal_entry.accounts[1].account == "VAT - SP"

# 		# Check if the credit amount for the second account is the VAT amount
# 		assert journal_entry.accounts[1].credit_in_account_currency == 15

# 	def test_custom_create_journal_entry_bts_allocates_correct_cost_center_to_tax_account(self):
# 		"""
# 		Test custom_create_journal_entry_bts creates a correct Journal Entry when custom_tax_account and custom_tax_rate_for_bank_recon are supplied
# 		"""
# 		bank_transaction = make_bank_transaction_test_record()

# 		# Set a specific cost center on "VAT - SP" GL account
# 		cost_center = make_new_cost_center()
# 		vat_account = frappe.get_doc("Account", "VAT - SP")
# 		vat_account.custom_cost_center_for_tax_account = cost_center.name
# 		vat_account.save()

# 		# Call the custom_create_journal_entry_bts function with test data
# 		custom_create_journal_entry_bts(
# 			bank_transaction_name=bank_transaction.name,
# 			reference_number=test_bank_transaction["description"],
# 			reference_date=test_bank_transaction["date"],
# 			posting_date=test_bank_transaction["date"],
# 			entry_type="Bank Entry",
# 			second_account="Telephone Expenses - SP",
# 			custom_tax_account="VAT - SP",
# 			custom_tax_rate_for_bank_recon=15,
# 			custom_cost_center_for_tax_account=cost_center.name,
# 		)

# 		# Fetch the created journal entry using the test transaction's description
# 		journal_entry = frappe.get_doc(
# 			"Journal Entry", {"cheque_no": test_bank_transaction["description"]}
# 		)

# 		# Check if the journal entry exists
# 		assert journal_entry

# 		# Check if the second account in the journal entry is "VAT - SP"
# 		assert journal_entry.accounts[1].account == "VAT - SP"

# 		# Check if the cost center for the second account is the cost center set up on the "VAT - SP" account
# 		assert journal_entry.accounts[1].cost_center == cost_center.name

# 	def test_custom_create_journal_entry_bts_calculates_vat_correctly_when_rate_is_not_supplied(self):
# 		"""
# 		Test custom_create_journal_entry_bts creates a correct Journal Entry when custom_tax_account and custom_tax_rate_for_bank_recon aren't supplied
# 		"""
# 		bank_transaction = make_bank_transaction_test_record()

# 		# Call the custom_create_journal_entry_bts function with test data
# 		custom_create_journal_entry_bts(
# 			bank_transaction_name=bank_transaction.name,
# 			reference_number=test_bank_transaction["description"],
# 			reference_date=test_bank_transaction["date"],
# 			posting_date=test_bank_transaction["date"],
# 			entry_type="Bank Entry",
# 			second_account="Telephone Expenses - SP",
# 		)

# 		# Fetch the created journal entry using the test transaction's description
# 		journal_entry = frappe.get_doc(
# 			"Journal Entry", {"cheque_no": test_bank_transaction["description"]}
# 		)

# 		# Check if the journal entry exists
# 		assert journal_entry

# 		# Check if the first account in the journal entry is "Telephone Expenses - SP", as per the test data
# 		assert journal_entry.accounts[0].account == "Telephone Expenses - SP"

# 		# Check if the credit amount for the first account is the total amount
# 		assert journal_entry.accounts[0].credit_in_account_currency == 115

# 		# Check if the second account in the journal entry is "VAT - SP"
# 		assert journal_entry.accounts[1].account != "VAT - SP"

# 	def test_custom_create_journal_entry_bts_adds_cost_center(self):
# 		"""
# 		Test custom_create_journal_entry_bts adds Cost Center to the acounts in the created Journal Entry
# 		"""
# 		bank_transaction = make_bank_transaction_test_record()
# 		cost_center = make_new_cost_center()

# 		# Call the custom_create_journal_entry_bts function with test data
# 		custom_create_journal_entry_bts(
# 			bank_transaction_name=bank_transaction.name,
# 			reference_number=test_bank_transaction["description"],
# 			reference_date=test_bank_transaction["date"],
# 			posting_date=test_bank_transaction["date"],
# 			entry_type="Bank Entry",
# 			second_account="Telephone Expenses - SP",
# 			cost_center=cost_center.name,
# 		)

# 		# Fetch the created journal entry using the test transaction's description
# 		journal_entry = frappe.get_doc(
# 			"Journal Entry", {"cheque_no": test_bank_transaction["description"]}
# 		)

# 		# Check if the journal entry exists
# 		assert journal_entry

# 		# Check if the all accounts in the journal entry has the correct Cost Center set
# 		for account in journal_entry.accounts:
# 			assert account.cost_center == cost_center.name


# def make_bank_transaction_test_record():
# 	doc = frappe.get_doc(test_bank_transaction).insert()
# 	doc.submit()
# 	return doc


# def make_new_cost_center():
# 	default_cost_center = frappe.get_doc(
# 		"Cost Center", get_default_cost_center(company=get_default_company())
# 	)
# 	if not frappe.db.exists("Cost Center", {"cost_center_name": "Test Cost Center"}):
# 		cost_center = frappe.new_doc("Cost Center")
# 		cost_center.cost_center_name = "Test Cost Center"
# 		cost_center.parent_cost_center = default_cost_center.parent_cost_center
# 		cost_center.insert(ignore_if_duplicate=True)
# 	else:
# 		cost_center = frappe.get_doc("Cost Center", {"cost_center_name": "Test Cost Center"})
# 	return cost_center
