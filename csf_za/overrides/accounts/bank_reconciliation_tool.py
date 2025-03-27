import json

import frappe
from erpnext import get_default_cost_center
from erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool import (
	reconcile_vouchers,
)
from erpnext.setup.utils import get_exchange_rate
from frappe import _
from frappe.utils import flt


@frappe.whitelist()
def custom_create_journal_entry_bts(
	bank_transaction_name,
	reference_number=None,
	reference_date=None,
	posting_date=None,
	entry_type=None,
	second_account=None,
	mode_of_payment=None,
	party_type=None,
	party=None,
	allow_edit=None,
	# ================================================================================================= #
	# ==================================== Custom code starts here ==================================== #
	# ================================================================================================= #
	cost_center=None,
	custom_tax_account=None,
	custom_tax_rate_for_bank_recon=None,
	custom_cost_center_for_tax_account=None,
):
	"""
	Override erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.create_journal_entry_bts
	to:
	        - Accept extra arguments
	        - Add a third leg to the Journal Entry for Value-added Tax, essentially
	          splitting the second_account_dict into two accounts
	"""
	# ================================================================================================= #
	# ===================================== Custom code ends here ===================================== #
	# ================================================================================================= #

	# Create a new journal entry based on the bank transaction
	bank_transaction = frappe.db.get_values(
		"Bank Transaction",
		bank_transaction_name,
		fieldname=["name", "deposit", "withdrawal", "bank_account", "currency"],
		as_dict=True,
	)[0]
	company_account = frappe.get_value("Bank Account", bank_transaction.bank_account, "account")
	account_type = frappe.db.get_value("Account", second_account, "account_type")
	if account_type in ["Receivable", "Payable"]:
		if not (party_type and party):
			frappe.throw(
				_("Party Type and Party is required for Receivable / Payable account {0}").format(
					second_account
				)
			)

	company = frappe.get_value("Account", company_account, "company")
	company_default_currency = frappe.get_cached_value("Company", company, "default_currency")
	company_account_currency = frappe.get_cached_value("Account", company_account, "account_currency")
	second_account_currency = frappe.get_cached_value("Account", second_account, "account_currency")

	# determine if multi-currency Journal or not
	is_multi_currency = (
		True
		if company_default_currency != company_account_currency
		or company_default_currency != second_account_currency
		or company_default_currency != bank_transaction.currency
		else False
	)

	accounts = []
	second_account_dict = {
		"account": second_account,
		"account_currency": second_account_currency,
		"credit_in_account_currency": bank_transaction.deposit,
		"debit_in_account_currency": bank_transaction.withdrawal,
		"party_type": party_type,
		"party": party,
		# ================================================================================================= #
		# ==================================== Custom code starts here ==================================== #
		# ================================================================================================= #
		# Original:
		# "cost_center": get_default_cost_center(company),
		"cost_center": cost_center or get_default_cost_center(company),
		# ================================================================================================= #
		# ===================================== Custom code ends here ===================================== #
		# ================================================================================================= #
	}

	company_account_dict = {
		"account": company_account,
		"account_currency": company_account_currency,
		"bank_account": bank_transaction.bank_account,
		"credit_in_account_currency": bank_transaction.withdrawal,
		"debit_in_account_currency": bank_transaction.deposit,
		# ================================================================================================= #
		# ==================================== Custom code starts here ==================================== #
		# ================================================================================================= #
		# Original:
		# "cost_center": get_default_cost_center(company),
		"cost_center": cost_center or get_default_cost_center(company),
		# ================================================================================================= #
		# ===================================== Custom code ends here ===================================== #
		# ================================================================================================= #
	}

	# convert transaction amount to company currency
	if is_multi_currency:
		exc_rate = get_exchange_rate(bank_transaction.currency, company_default_currency, posting_date)
		withdrawal_in_company_currency = flt(exc_rate * abs(bank_transaction.withdrawal))
		deposit_in_company_currency = flt(exc_rate * abs(bank_transaction.deposit))
	else:
		withdrawal_in_company_currency = bank_transaction.withdrawal
		deposit_in_company_currency = bank_transaction.deposit

	# if second account is of foreign currency, convert and set debit and credit fields.
	if second_account_currency != company_default_currency:
		exc_rate = get_exchange_rate(second_account_currency, company_default_currency, posting_date)
		second_account_dict.update(
			{
				"exchange_rate": exc_rate,
				"credit": deposit_in_company_currency,
				"debit": withdrawal_in_company_currency,
				"credit_in_account_currency": flt(deposit_in_company_currency / exc_rate) or 0,
				"debit_in_account_currency": flt(withdrawal_in_company_currency / exc_rate) or 0,
			}
		)
	else:
		second_account_dict.update(
			{
				"exchange_rate": 1,
				"credit": deposit_in_company_currency,
				"debit": withdrawal_in_company_currency,
				"credit_in_account_currency": deposit_in_company_currency,
				"debit_in_account_currency": withdrawal_in_company_currency,
			}
		)

	# if company account is of foreign currency, convert and set debit and credit fields.
	if company_account_currency != company_default_currency:
		exc_rate = get_exchange_rate(company_account_currency, company_default_currency, posting_date)
		company_account_dict.update(
			{
				"exchange_rate": exc_rate,
				"credit": withdrawal_in_company_currency,
				"debit": deposit_in_company_currency,
			}
		)
	else:
		company_account_dict.update(
			{
				"exchange_rate": 1,
				"credit": withdrawal_in_company_currency,
				"debit": deposit_in_company_currency,
				"credit_in_account_currency": withdrawal_in_company_currency,
				"debit_in_account_currency": deposit_in_company_currency,
			}
		)

	# ================================================================================================= #
	# ==================================== Custom code starts here ==================================== #
	# ================================================================================================= #
	# Handle scenario where a custom_tax_account and custom_tax_rate_for_bank_recon were supplied
	if custom_tax_account and custom_tax_rate_for_bank_recon:
		custom_tax_rate_for_bank_recon = float(custom_tax_rate_for_bank_recon)
		# Add second account, but subtract the tax
		accounts.append(
			{
				"account": second_account,
				"credit_in_account_currency": round(
					bank_transaction.deposit * 100 / (100 + custom_tax_rate_for_bank_recon), 2
				),
				"debit_in_account_currency": round(
					bank_transaction.withdrawal * 100 / (100 + custom_tax_rate_for_bank_recon), 2
				),
				"party_type": party_type,
				"party": party,
				"cost_center": cost_center or get_default_cost_center(company),
			}
		)
		# Add the tax to the provided tax account
		accounts.append(
			{
				"account": custom_tax_account,
				"credit_in_account_currency": round(
					bank_transaction.deposit
					* custom_tax_rate_for_bank_recon
					/ (100 + custom_tax_rate_for_bank_recon),
					2,
				),
				"debit_in_account_currency": round(
					bank_transaction.withdrawal
					* custom_tax_rate_for_bank_recon
					/ (100 + custom_tax_rate_for_bank_recon),
					2,
				),
				"party_type": party_type,
				"party": party,
				"cost_center": custom_cost_center_for_tax_account,
			}
		)
	else:
		# ================================================================================================= #
		# ===================================== Custom code ends here ===================================== #
		# ================================================================================================= #
		accounts.append(second_account_dict)
	accounts.append(company_account_dict)

	journal_entry_dict = {
		"voucher_type": entry_type,
		"company": company,
		"posting_date": posting_date,
		"cheque_date": reference_date,
		"cheque_no": reference_number,
		"mode_of_payment": mode_of_payment,
	}
	if is_multi_currency:
		journal_entry_dict.update({"multi_currency": True})

	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.update(journal_entry_dict)
	journal_entry.set("accounts", accounts)

	if allow_edit:
		return journal_entry

	journal_entry.insert()
	journal_entry.submit()

	if bank_transaction.deposit > 0.0:
		paid_amount = bank_transaction.deposit
	else:
		paid_amount = bank_transaction.withdrawal

	vouchers = json.dumps(
		[
			{
				"payment_doctype": "Journal Entry",
				"payment_name": journal_entry.name,
				"amount": paid_amount,
			}
		]
	)

	return reconcile_vouchers(bank_transaction_name, vouchers)
