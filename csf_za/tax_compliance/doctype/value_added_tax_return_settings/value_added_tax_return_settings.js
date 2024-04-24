// Copyright (c) 2024, Dirk van der Laarse and contributors
// For license information, please see license.txt

frappe.ui.form.on("Value-added Tax Return Settings", {
	refresh(frm) {
		frm.trigger('set_intro_text');
		frm.trigger('set_queries');

		if (frm.doc.company && frm.doc.tax_accounts.length === 0) {
			frm.trigger("auto_set_tax_accounts");
		}

	},
	set_intro_text(frm){
		intro_text = `
			<div>
				${__("When submitting your VAT201 return, your VAT-related transactions need to be classified")}:
				<h5>${__("Output Tax")}</h5>
				<ol type="A">
					<li>
						<b>${__("Standard rate (excl capital goods/services and accommodation)")}</b>
						<details>
							${__("Examples of standard rated sales are")}:<br>
							A) ${__("Aircraft fuel")};<br>
							B) ${__("Building materials and services")};<br>
							C) ${__("Books and newspapers")};<br>
							D) ${__("Cigarettes, cold drinks and liquor")};<br>
							E) ${__("Clothing")};<br>
							F) ${__("Electricity, water and refuse removal")};<br>
							G) ${__("Entrance fees to sporting events")};<br>
							H) ${__("Furniture")};<br>
							I) ${__("Hotel accommodation")};<br>
							J) ${__("Lawyer's services")};<br>
							K) ${__("Local air travel")};<br>
							L) ${__("Meat and any food served as a meal")};<br>
							M) ${__("Medicines")};<br>
							N) ${__("edical services (other than by State hospitals)")};<br>
							O) ${__("Motor repairs")};<br>
							P) ${__("Motor vehicles and spares")};<br>
							Q) ${__("Paraffin (excluding illuminating kerosene)")};<br>
							R) ${__("Postage stamps")};<br>
							S) ${__("Restaurant services")};<br>
							T) ${__("Telephone services")};<br>
							U) ${__("Transport of goods(local)")};<br>
							V) ${__("Washing powder")};<br>
							W) ${__("White bread")}.
						</details>
						
					</li>
					<li>
						<b>${__("Standard rate (only capital goods/services)")}</b>
						<details>
							${__("The VAT inclusive amount of goods and/or services supplied by you at the standard rate, only capital goods and/or services This reflects the consideration received (VAT included) in respect of")}:<br>
							A) ${__("Sale of capital goods and/or services (e.g. Sale of land and buildings, plant and machinery, intellectual property)")}.<br>
							B) ${__("VAT on assets upon termination of registration")}.
						</details>
					</li>
					<li>
						<b>${__("Zero Rated (excluding goods exported)")}</b>
						<details>
							${__("Goods and/or services supplied by you at zero rate, excluding exported goods. Zero rated supplies are taxable supplies, taxed at a rate of 0%. <br>Examples of zero-rated supplies are")}:<br>
							A) ${__("Brown bread")};<br>
							B) ${__("Eggs of domesticated chickens")};<br>
							C) ${__("Edible legumes and pulses of leguminous plants")};<br>
							D) ${__("Fresh/frozen fruit and vegetables")};<br>
							E) ${__("Dried beans")};<br>
							F) ${__("Illuminating kerosene")};<br>
							G) ${__("Lentils")};<br>
							H) ${__("Maize meal")};<br>
							I) ${__("Milk, cultured milk, milk powder and dairy powder blend")};<br>
							J) ${__("Pilchards/ sardines in tins or cans")};<br>
							K) ${__("Vegetable oil excluding olive oil")};<br>
							L) ${__("Fuel levy goods (e.g. petrol and diesel)")};<br>
							M) ${__("The sale of a business or part of a business as a going concern")};<br>
							N) ${__("Services supplied in respect of goods temporarily admitted into the RSA from an export country for the purposes of being repaired or serviced")}.<br>
							O) ${__("International travel")}.<br>
						</details>
					</li>
					<li>
						<b>${__("Zero Rated (only exported goods)")}</b>
						<details>
							${__("Goods supplied by you at the zero rate which has been exported from the RSA")}.
						</details>
					</li>
					<li>
						<b>${__("Exempt and non-supplies")}</b>
						<details>
							${__("Exempt supplies or non-supplies supplied by you. No output tax is levied in respect of exempt supplies and no input tax relating to the expenditure on these supplies may be deducted. The following are examples of exempt supplies")}:<br>
							A) ${__("Financial services")};<br>
							B) ${__("Donated goods or services by an association not for gain")};<br>
							C) ${__("Residential accommodation")};<br>
							D) ${__("The letting of leasehold land")};<br>
							E) ${__("The sale or letting of land situated outside the Republic")};<br>
							F) ${__("Transport of fare-paying passengers by road or railway")};<br>
							G) ${__("The supply of educational services")};<br>
							H) ${__("Membership contributions to employee organisations, such as trade unions")};<br>
							I) ${__("The supply of childcare services")}.<br>
						</details>
					</li>
				</ol>
				<h5>${__("Input Tax")}</h5>
				<ol type="A">
					<li>
						<b>${__("Other goods and/or services supplied to you (not capital goods)")}</b>
						<details>
							${__("Examples of standard rated purchases/acquisitions are")}:<br>
							A) ${__("Accounting fees")};<br>
							B) ${__("Advertisements")};<br>
							C) ${__("Commission paid")};<br>
							D) ${__("Cleaning materials")};<br>
							E) ${__("Short term insurance premiums")};<br>
							F) ${__("Membership fees")};<br>
							G) ${__("Rent")};<br>
							H) ${__("Repairs")}<br>
							I) ${__("Second-hand goods (notional input tax)")};<br>
							J) ${__("Stationery")};<br>
							K) ${__("Stock purchases")};<br>
							L) ${__("Telephone")};<br>
							M) ${__("Water and lights")}.<br>
						</details>
					</li>
					<li>
						<b>${__("Capital goods and/or services supplied to you (local)")}</b>
						<details>
							${__("The permissible VAT amount of capital goods and/or services supplied to you. The prescribed document, for example a valid tax invoice must be held by you before you complete any amount in this field. Examples of such acquisitions are")}:<br>
							A) ${__("Office equipment")};<br>
							B) ${__("Furniture")};<br>
							C) ${__("Trucks")};<br>
							D) ${__("Land and buildings")}.<br>
						</details>
					</li>
					<li>
						<b>${__("Capital goods imported by you")}</b>
						<details>
							${__("The permissible VAT amount of capital goods imported by you. The Customs Code field is mandatory. This field applies to capital goods imported in respect of which a bill of entry valid release document and receipt for the payment of the VAT issued by Customs, is held")}.
						</details>
					</li>
					<li>
						<b>${__("Other goods imported by you (not capital goods)")}</b>
						<details>
							${__("The permissible VAT amount of other goods imported by you (not capital goods). This applies to non-capital goods imported in respect of which a bill of entry ,valid release document and receipt for the payment of the VAT issued by Customs, is held. An example of such acquisition is the importation of trading stock")}.
						</details>
					</li>
				</ol>
			</div>
		</div>
		`
		frm.set_intro(intro_text, 'blue');
	},
	set_queries(frm) {
		fields = [
			"standard_rate_non_capital",
			"standard_rate_capital",
			"zero_rate_non_exported",
			"zero_rate_exported",
			"exempt",
			"goods_supplied",
			"goods_non_import",
			"goods_import",
			"other_goods_import",
		]
		fields.forEach(field => {
			frm.set_query(field, () => {
				return {
					filters: {
						company: ["=", frm.doc.name],
					},
				};
			});
		});
	},
	transaction_classification(frm) {
		if (frm.doc.transaction_classification) {
			if (frm.doc.transaction_classification === "General Ledger Accounts") {
				frm.set_value("output_tax_doctype", "Account");
				frm.set_value("input_tax_doctype", "Account");
			}
			else if (frm.doc.transaction_classification === "Taxes and Charges Templates") {
				frm.set_value("output_tax_doctype", "Sales Taxes and Charges Template");
				frm.set_value("input_tax_doctype", "Purchase Taxes and Charges Template");
			}
		}
	},
	button_classifications_report(frm) {
		// Open the 'Account Classifications for VAT Return' Report
		frappe.route_options = {
			"company": frm.doc.company
		};
		frappe.set_route("query-report", "Account Classifications for VAT Return");
	},
	company(frm) {
		// Trigger when company is changed
		frm.trigger("auto_set_tax_accounts");
	},
	auto_set_tax_accounts(frm) {
		// Auto-populate the Tax Accounts field based on existing Accounts with Account Type set to Tax
		frappe.db.get_list('Account',
			{fields: ['name'], filters:{"account_type": "Tax", "company": frm.doc.company}}).then((res) => {
				frm.clear_table("tax_accounts");
				res.forEach((account) => {
					let row = frm.add_child("tax_accounts");
					row.account = account.name
				});
				frm.refresh_field("tax_accounts");
			});		
	}
});
