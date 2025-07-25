# Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# Modified by dvanderlaarse
# Code mainly copied from erpnext/accounts/doctype/process_statement_of_accounts/process_statement_of_accounts.py
# Modified to accept First National Bank statement type 'as is'

from datetime import datetime

import frappe
from erpnext.accounts.doctype.bank_statement_import.bank_statement_import import (
	BankStatementImport,
)
from frappe import _
from frappe.utils.csvutils import read_csv_content, to_csv


class CustomBankStatementImport(BankStatementImport):
	def validate(self):
		self.modify_uploaded_bank_statement()
		super().validate()

	@frappe.whitelist()
	def modify_uploaded_bank_statement(self):
		"""
		Modify an uploaded bank statement if conditions are met.
		Splits the Amount column into Deposit and Withdrawal columns.
		"""
		if self.import_file and not self.import_file.endswith("_modified.csv"):
			custom_template = frappe.get_value("Bank", self.bank, "custom_bank_statement_template")
			if custom_template:
				frappe.msgprint(
					_("The uploaded file will be modified: the Amount column will be split in two")
				)
				self.remove_null_bytes()
				file_doc = frappe.get_doc("File", {"file_url": self.import_file})
				self.validate_import_file_is_csv(file_doc)

				bank_template_map = {
					"First National Bank": self.parse_csv_file_fnb,
					"Bank Zero": self.parse_csv_file_bankzero,
					"Capitec": self.parse_csv_file_capitec,
					"Nedbank": self.parse_csv_file_nedbank,
					"Standard Bank": self.parse_csv_file_standard_bank,
					"ABSA": self.parse_csv_file_absa,
				}
				if custom_template in bank_template_map:
					bank_template_map[custom_template](file_doc)
				else:
					frappe.throw(_("Unsupported bank template"))
			return self.import_file

	def validate_import_file_is_csv(self, file_doc=None):
		"""
		Check if the given file_doc has a .csv extension.
		"""
		if file_doc:
			_, extension = file_doc.get_extension()
			if extension.lower() != ".csv":
				frappe.throw(_("Import file should be of type .csv"), title=_("File Type Error"))
		else:
			frappe.throw(_("File doc not found"))

	def _save_modified_csv(self, original_file_doc, file_data):
		"""
		Save the modified CSV content as a new File document and update self.import_file.
		"""
		file_name, _ = original_file_doc.get_extension()
		new_file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"{file_name}_modified.csv",
				"attached_to_doctype": "Bank Statement Import",
				"attached_to_name": self.name,
				"folder": "Home",
				"content": file_data,
				"is_private": 1,
			}
		)
		new_file.save()
		self.import_file = new_file.file_url

	def _split_amount(self, amount_value):
		"""
		Split the amount into deposit and withdrawal.
		"""
		if amount_value < 0:
			return 0, abs(amount_value)
		return amount_value, 0

	def _parse_date(self, date_str, formats=None):
		"""
		Attempt to parse a date string using the provided formats.
		"""
		if not formats:
			formats = ["%Y-%m-%d", "%Y/%m/%d"]
		for fmt in formats:
			try:
				date_obj = datetime.strptime(date_str, fmt)
				return date_obj.strftime("%Y-%m-%d")
			except ValueError:
				continue
		frappe.throw(_("Invalid date format: {0}").format(date_str))

	def parse_csv_file_fnb(self, file_doc):
		"""
		Process a CSV file for First National Bank and split the Amount column.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		expected_headers = [
			"Date",
			"SERVICE FEE",
			"Amount",
			"DESCRIPTION",
			"REFERENCE",
			"Balance",
			"CHEQUE NUMBER",
			None,
		]
		if data[2][:6] != expected_headers[:6]:
			frappe.throw(
				_("Unexpected headers in CSV. Expected: {0} in third row").format(
					", ".join(expected_headers[:6])
				)
			)

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		for row_num, row in enumerate(data[3:], start=1):
			try:
				amount_value = float(row[2])
			except ValueError:
				frappe.throw(_("Invalid Amount value found in row {0}").format(row_num))
			deposit, withdrawal = self._split_amount(amount_value)
			date_str = self._parse_date(row[0])
			new_row = [date_str, row[3], row[4], deposit, withdrawal, self.bank_account]
			new_data.append(new_row)

		file_data = to_csv(new_data)
		self._save_modified_csv(file_doc, file_data)

	def parse_csv_file_bankzero(self, file_doc):
		"""
		Process a CSV file for Bank Zero and split the Amount column.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		expected_headers = [
			"Date",
			"Day",
			"Time",
			"Type",
			"Description 1",
			"Description 2",
			"Fee",
			"Amount",
			"Balance",
			"Has Attachments",
		]
		if data[0][:9] != expected_headers[:9]:
			frappe.throw(
				_("Unexpected headers in CSV. Expected: {0} in first row").format(
					", ".join(expected_headers[:9])
				)
			)

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		for row_num, row in enumerate(data[1:], start=1):
			try:
				amount_value = float(row[7].replace(" ", ""))
			except ValueError:
				frappe.throw(_("Invalid Amount value found in row {0}").format(row_num))
			deposit, withdrawal = self._split_amount(amount_value)
			date_str = self._parse_date(row[0])
			new_row = [date_str, row[4], row[5], deposit, withdrawal, self.bank_account]
			new_data.append(new_row)

		file_data = to_csv(new_data)
		self._save_modified_csv(file_doc, file_data)

	def parse_csv_file_capitec(self, file_doc):
		"""
		Process a CSV file for Capitec and split the Amount column.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		expected_headers = [
			"Account",
			"Date",
			"Description",
			"Reference",
			"Amount",
			"Fees",
			"Balance",
		]
		if data[2][:7] != expected_headers:
			frappe.throw(_("Unexpected headers in CSV. Expected: {0}").format(", ".join(expected_headers)))
		if not data:
			frappe.throw(_("No valid data rows found in the CSV."))

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		for row_num, row in enumerate(data[3:], start=1):
			if row[0] == "Total:":
				break
			if len(row) < 5:
				frappe.throw(_("Row {0} has insufficient columns.").format(row_num))

			date_str = self._parse_date(row[1], formats=["%d/%m/%Y"])

			# If amount is None, but there is a value in "Fees", we can safely skip
			if row[4] == None and row[5] != None:
				continue
			try:
				amount_value = float(row[4])
			except ValueError:
				frappe.throw(_("Invalid Amount in row {0}: '{1}'").format(row_num, row[4]))
			deposit, withdrawal = self._split_amount(amount_value)
			new_row = [date_str, row[2], row[3], deposit, withdrawal, self.bank_account]
			new_data.append(new_row)

			# Create a new row if this row has a fee
			print(f"\n\n{row[5]}\n\n")
			if row[5] != None and float(row[5]) != 0:
				try:
					fee_value = float(row[5])
				except ValueError:
					frappe.throw(_("Invalid Amount in row {0}: '{1}'").format(row_num, row[5]))
				fee_deposit, fee_withdrawal = self._split_amount(fee_value)
				new_row = [
					date_str,
					f"Fee - {row[2]}",
					f"Fee - {row[3]}",
					fee_deposit,
					fee_withdrawal,
					self.bank_account,
				]
				new_data.append(new_row)

		file_data = to_csv(new_data)
		self._save_modified_csv(file_doc, file_data)

	def parse_csv_file_nedbank(self, file_doc):
		"""
		Process a CSV file for Nedbank and split the Amount column.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		if not data:
			frappe.throw(_("No valid data rows found in the CSV."))

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		running_balance = 0
		for row_num, row in enumerate(data[5:], start=1):
			if len(row) < 4:
				frappe.throw(_("Row {0} has insufficient columns.").format(row_num))
			# Skip rows with blank Amounts that do not change the running balance
			if row[2] == None and row[3] == running_balance:
				continue

			# Skip unwanted rows
			if row[1] in ["CARRIED FORWARD", "BROUGHT FORWARD", "PROVISIONAL STATEMENT"]:
				continue

			date_str = self._parse_date(row[0], formats=["%d%b%Y"])
			try:
				amount_value = float(row[2])
			except (ValueError, TypeError):
				frappe.throw(_("Invalid Amount in row {0}: '{1}'").format(row_num, row[2]))
			deposit, withdrawal = self._split_amount(amount_value)
			running_balance = row[3]
			new_row = [date_str, row[1], row[1], deposit, withdrawal, self.bank_account]
			new_data.append(new_row)

		file_data = to_csv(new_data)
		self._save_modified_csv(file_doc, file_data)

	def parse_csv_file_standard_bank(self, file_doc):
		"""
		Process a CSV file for Standard Bank and split the Amount column.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		if not data:
			frappe.throw(_("No valid data rows found in the CSV."))

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		for row_num, row in enumerate(data[15:], start=1):
			if row[3].startswith("CLOSE BALANCE"):
				break
			if row[3].startswith("OPEN BALANCE"):
				continue
			if len(row) < 10:
				frappe.throw(_("Row {0} has insufficient columns.").format(row_num))

			date_str = self._parse_date(row[0], formats=["%Y/%m/%d"])
			try:
				amount_value = float(row[4])
			except (ValueError, TypeError):
				frappe.throw(_("Invalid Amount in row {0}: '{1}'").format(row_num, row[4]))
			deposit, withdrawal = self._split_amount(amount_value)
			new_row = [date_str, row[3], row[7], deposit, withdrawal, self.bank_account]
			new_data.append(new_row)

		file_data = to_csv(new_data)
		self._save_modified_csv(file_doc, file_data)

	def parse_csv_file_absa(self, file_doc):
		"""
		Process a CSV file for ABSA and split the Amount column.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		if not data:
			frappe.throw(_("No valid data rows found in the CSV."))

		expected_headers = ["Date", "Description", "Amount", "Balance"]
		if data[0][:4] != expected_headers:
			frappe.throw(_("Unexpected headers in CSV. Expected: {0}").format(", ".join(expected_headers)))

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		for row_num, row in enumerate(data[1:], start=1):
			if len(row) < 4:
				frappe.throw(_("Row {0} has insufficient columns.").format(row_num))
			try:
				date_obj = datetime.strptime(row[0], "%Y%m%d")
				date_str = date_obj.strftime("%Y-%m-%d")
			except ValueError:
				frappe.throw(_("Invalid date format in row {0}: '{1}'").format(row_num, row[0]))
			try:
				amount_value = float(row[2])
			except ValueError:
				frappe.throw(_("Invalid Amount in row {0}: '{1}'").format(row_num, row[2]))
			deposit, withdrawal = self._split_amount(amount_value)
			new_row = [date_str, row[1], row[1], deposit, withdrawal, self.bank_account]
			new_data.append(new_row)

		file_data = to_csv(new_data)
		self._save_modified_csv(file_doc, file_data)

	def remove_null_bytes(self):
		"""
		Remove all null bytes from the input file and write the cleaned data to the output file.
		"""
		if (
			self.import_file
			and self.bank == "First National Bank"
			and self.import_file[-12:] != "_cleaned.csv"
		):
			file_doc = frappe.get_doc("File", {"file_url": self.import_file})
			file_content = file_doc.get_content()

			file_content = file_content.replace("\x00", "")

			file_name, extension = file_doc.get_extension()
			_file = frappe.get_doc(
				{
					"doctype": "File",
					"file_name": file_name + "_cleaned.csv",
					"attached_to_doctype": "Bank Statement Import",
					"attached_to_name": self.name,
					"folder": "Home",
					"content": file_content,
					"is_private": 1,
				}
			)
			_file.save()
			self.import_file = _file.file_url


@frappe.whitelist()
def custom_get_preview_from_template(data_import, import_file=None, google_sheets_url=None):
	"""
	Override get_preview_from_template to only generate a preview of the bank statement import data
	if there are no nulls in the content.
	"""
	file_doc = frappe.get_doc("File", {"file_url": import_file})
	file_content = file_doc.get_content()
	contains_nulls = file_content.find("\x00")

	if contains_nulls == -1:
		return frappe.get_doc("Bank Statement Import", data_import).get_preview_from_template(
			import_file, google_sheets_url
		)
	else:
		return {"columns": [], "data": [], "warnings": []}
