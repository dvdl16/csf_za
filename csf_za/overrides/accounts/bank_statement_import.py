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
		Perform a series of operations to modify an uploaded bank statement file if certain conditions are met.
		If the bank is "First National Bank" or "Bank Zero", and the import file is not already marked as modified
		(indicated by not having "_modified.csv" at the end of the file name), the function proceeds
		to split the Amount column in the CSV file into separate Deposit and Withdrawal columns.
		"""
		if self.import_file and self.import_file[-13:] != "_modified.csv":
			if self.bank in ["First National Bank", "Bank Zero"]:
				frappe.msgprint(
					_("The uploaded file will be modified: the Amount column will be split in two")
				)

				self.remove_null_bytes()
				file_doc = frappe.get_doc("File", {"file_url": self.import_file})
				self.validate_import_file_is_csv(file_doc)
				if self.bank == "First National Bank":
					self.split_amount_column_in_csv_file_fnb(file_doc)
				elif self.bank == "Bank Zero":
					self.split_amount_column_in_csv_file_bankzero(file_doc)
				return self.import_file

	def validate_import_file_is_csv(self, file_doc=None):
		"""
		Checks whether the given file_doc has a .csv extension.
		"""
		if file_doc:
			file_name, extension = file_doc.get_extension()
			error_title = _("File Type Error")
			if extension != ".csv":
				frappe.throw(_("Import file should be of type .csv"), title=error_title)
		else:
			frappe.throw(_("File doc not found"))

	def split_amount_column_in_csv_file_fnb(self, file_doc):
		"""
		Process a given CSV file containing bank statement data, and modifies it to split
		the "Amount" column into separate "Deposit" and "Withdrawal" columns.

		The function assumes that the input CSV file has specific headers in the third row,
		and it validates the format of the date and amount values in each row.

		Finally, the function saves the modified CSV file and updates the file URL.
		"""
		file_content = file_doc.get_content()
		data = read_csv_content(file_content)

		# Find the header row dynamically
        	header_row_index = None
        	for i, row in enumerate(data):
            		if "Date" in row and "Amount" in row and "Description" in row:
                	header_row_index = i
                break
        
        	if header_row_index is None:
            		frappe.throw("Could not find a valid header row in the CSV file.")

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
        
        	for row in data[header_row_index + 1:]:
            		try:
                	amount_value = float(row[2])
            	except ValueError:
                	frappe.throw("Invalid Amount value found in row {}".format(row))
            
            	deposit = amount_value if amount_value > 0 else 0
            	withdrawal = -amount_value if amount_value < 0 else 0
            
            	try:
                	date = datetime.strptime(row[0], "%Y-%m-%d").strftime("%Y-%m-%d")
            	except ValueError:
                	frappe.throw("Invalid date format in row {}".format(row))
            
            new_row = [date, row[3], row[4], deposit, withdrawal, self.bank_account]
            new_data.append(new_row)
        
        file_data = to_csv(new_data)
        file_name, _ = file_doc.get_extension()
        _file = frappe.get_doc(
            {
                "doctype": "File",
                "file_name": file_name + "_modified.csv",
                "attached_to_doctype": "Bank Statement Import",
                "attached_to_name": self.name,
                "folder": "Home",
                "content": file_data,
                "is_private": 1,
            }
        )
        _file.save()
        self.import_file = _file.file_url

	def split_amount_column_in_csv_file_bankzero(self, file_doc):
		"""
		Process a given CSV file containing bank statement data, and modifies it to split
		the "Amount" column into separate "Deposit" and "Withdrawal" columns.

		The function assumes that the input CSV file has specific headers in the first row,
		and it validates the format of the date and amount values in each row.

		Finally, the function saves the modified CSV file and updates the file URL.
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
				f"Unexpected headers found in .csv file. Expected: {', '.join(expected_headers[:9])} in first row"
			)

		new_data = [["Date", "Description", "Reference Number", "Deposit", "Withdrawal", "Bank Account"]]
		for row_num, row in enumerate(data[1:], start=1):
			amount_value = None
			try:
				amount_value = float(row[7].replace(" ", ""))
			except ValueError:
				frappe.throw(f"Invalid Amount value found in row {row_num}")

			deposit, withdrawal = (0, 0)
			bank_account = self.bank_account
			date = None
			if amount_value < 0:
				withdrawal = amount_value * -1
			else:
				deposit = amount_value

			# Parse date format as YYYY-MM-DD
			try:
				date = datetime.strptime(row[0], "%Y-%m-%d")
			except ValueError:
				try:
					date = datetime.strptime(row[0], "%Y/%m/%d")
				except ValueError:
					frappe.throw(f"Invalid date value found in row {row_num}")

			new_row = [date.strftime("%Y-%m-%d"), row[4], row[5], deposit, withdrawal, bank_account]
			new_data.append(new_row)

		file_data = to_csv(new_data)
		file_name, extension = file_doc.get_extension()
		_file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": file_name + "_modified.csv",
				"attached_to_doctype": "Bank Statement Import",
				"attached_to_name": self.name,
				"folder": "Home",
				"content": file_data,
				"is_private": 1,
			}
		)
		_file.save()
		self.import_file = _file.file_url

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
