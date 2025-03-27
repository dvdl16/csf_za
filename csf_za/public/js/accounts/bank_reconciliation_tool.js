/*
Override Bank Reconciliation Tool to change the "Cost Center" field on the "Actions" Dialog
to be Mandatory when "Action" is set to "Create Voucher", and to have a default value as 
set on the "Bank Account".
 */

// Turn off the default "render" function on "Bank Reconciliation Tool"
frappe.ui.form.off('Bank Reconciliation Tool', 'render');

// Override the default "render" function on "Bank Reconciliation Tool" to our "custom_render" function
frappe.ui.form.on(
  'Bank Reconciliation Tool',
  'render',
  custom_render
);

function custom_render(frm) {
    // This is the custom "render" function for the "Bank Reconciliation Tool" doctype.
    // Modified from the original erpnext/accounts/doctype/bank_reconciliation_tool/bank_reconciliation_tool.js
    //
    // Extend the erpnext.accounts.bank_reconciliation.DataTableManager class and extend the
    // erpnext.accounts.bank_reconciliation.DialogManager class

    // ================================================================================================= //
	// ==================================== Custom code starts here ==================================== //
	// ================================================================================================= //
    console.log("csf_za: Overriding 'render' function on 'Bank Reconciliation Tool'");

    // Extend the DialogManager class
    erpnext.accounts.bank_reconciliation.DialogManager = class DialogManager extends erpnext.accounts.bank_reconciliation.DialogManager {
        // Modified from the original erpnext/public/js/bank_reconciliation_tool/dialog_manager.js
        // 
        // Override the get_voucher_fields method to return a list of the original voucher fields,
        // as well as our own custom fields
        get_voucher_fields() {           
            // Call the original get_voucher_fields method to get the voucher fields
            let voucherFields = super.get_voucher_fields();

            // Now we add our own fields to the voucherFields list
            if (!voucherFields.find(obj => obj.fieldname === "custom_tax_section")){
                const newFields = [
                // A section break to for improved layout
                {
                    fieldtype: "Section Break",
                    fieldname: "custom_tax_section",
                    label: "Tax Details",
                    depends_on:
                        "eval:doc.action=='Create Voucher' &&  doc.document_type=='Journal Entry'"
                },
    
                // The rate that should be used to calculate the amount for the third account/tax account
                // in the Journal Entry
                {
                    fieldtype: "Float",
                    fieldname: "custom_tax_rate_for_bank_recon",
                    label: "Rate (%)",
                    depends_on:
                        "eval:doc.action=='Create Voucher' &&  doc.document_type=='Journal Entry'"
                },
    
                // The Account that should be used as the third account/tax account in the Journal Entry
                {
                    fieldname: "custom_tax_account",
                    fieldtype: "Link",
                    label: "Tax Account",
                    options: "Account",
                    get_query: () => {
                        return {
                            filters: {
                                is_group: 0,
                                company: this.company,
                            },
                        };
                    }
                },
    
                // The Cost Center that should be used for the tax account in the Journal Entry
                {
                    fieldname: "custom_cost_center_for_tax_account",
                    fieldtype: "Link",
                    label: "Cost Center for Tax Account",
                    options: "Cost Center"
                },
    
                // HTML field to preview the Journal Entry
                {
                    fieldname: "custom_tax_preview",
                    fieldtype: "HTML",
                    label: "Journal Entry Preview",
                    options: ""
                }]
    
                // Inject these new fields into the existing fields list
                const costCenterFieldIndex = voucherFields.findIndex(field => field.fieldname === "cost_center");
                newFields.slice().reverse().forEach(newField => {
                    if (costCenterFieldIndex !== -1) {
                        voucherFields.splice(costCenterFieldIndex + 1, 0, newField);
                    }
                })

            }

            return voucherFields;
        }
        // ================================================================================================= //
        // ===================================== Custom code ends here ===================================== //
        // ================================================================================================= //


        // Override the add_journal_entry method to pass our custom fields as additional paramters
        add_journal_entry(values) {
            frappe.call({
                method:
                    "erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.create_journal_entry_bts",
                args: {
                    bank_transaction_name: this.bank_transaction.name,
                    reference_number: values.reference_number,
                    reference_date: values.reference_date,
                    party_type: values.party_type,
                    party: values.party,
                    posting_date: values.posting_date,
                    mode_of_payment: values.mode_of_payment,
                    entry_type: values.journal_entry_type,
                    second_account: values.second_account,
                    // ================================================================================================= //
                    // ==================================== Custom code starts here ==================================== //
                    // ================================================================================================= //                    
                    cost_center: values.cost_center,
                    custom_tax_account: values.custom_tax_account,
                    custom_tax_rate_for_bank_recon: values.custom_tax_rate_for_bank_recon,
                    custom_cost_center_for_tax_account: values.custom_cost_center_for_tax_account
                    // ================================================================================================= //
                    // ===================================== Custom code ends here ===================================== //
                    // ================================================================================================= //
            },
                callback: (response) => {
                    const alert_string = __("Bank Transaction {0} added as Journal Entry", [this.bank_transaction.name]);
                    frappe.show_alert(alert_string);
                    this.update_dt_cards(response.message);
                    this.dialog.hide();
                },
            });
        }

        // Override the edit_in_full_page method to pass our custom fields as additional paramters
        edit_in_full_page() {
            const values = this.dialog.get_values(true);
            if (values.document_type == "Payment Entry") {
                frappe.call({
                    method:
                        "erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.create_payment_entry_bts",
                    args: {
                        bank_transaction_name: this.bank_transaction.name,
                        reference_number: values.reference_number,
                        reference_date: values.reference_date,
                        party_type: values.party_type,
                        party: values.party,
                        posting_date: values.posting_date,
                        mode_of_payment: values.mode_of_payment,
                        project: values.project,
                        cost_center: values.cost_center,
                        allow_edit: true
                    },
                    callback: (r) => {
                        const doc = frappe.model.sync(r.message);
                        frappe.set_route("Form", doc[0].doctype, doc[0].name);
                    },
                });
            } else {
                frappe.call({
                    method:
                        "erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.create_journal_entry_bts",
                    args: {
                        bank_transaction_name: this.bank_transaction.name,
                        reference_number: values.reference_number,
                        reference_date: values.reference_date,
                        party_type: values.party_type,
                        party: values.party,
                        posting_date: values.posting_date,
                        mode_of_payment: values.mode_of_payment,
                        entry_type: values.journal_entry_type,
                        second_account: values.second_account,
                        allow_edit: true,
                        // ================================================================================================= //
                        // ==================================== Custom code starts here ==================================== //
                        // ================================================================================================= //
                        cost_center: values.cost_center,
                        custom_tax_account: values.custom_tax_account,
                        custom_tax_rate_for_bank_recon: values.custom_tax_rate_for_bank_recon,
                        custom_cost_center_for_tax_account: values.custom_cost_center_for_tax_account
                        // ================================================================================================= //
                        // ===================================== Custom code ends here ===================================== //
                        // ================================================================================================= //
                    },
                    callback: (r) => {
                        var doc = frappe.model.sync(r.message);
                        frappe.set_route("Form", doc[0].doctype, doc[0].name);
                    },
                });
            }
        }


    }

    erpnext.accounts.bank_reconciliation.DataTableManager = class DataTableManager extends erpnext.accounts.bank_reconciliation.DataTableManager {
        // Modified from the original erpnext/public/js/bank_reconciliation_tool/data_table_manager.js
        //
        // Override the "set_listeners" function to change meta properties on some of the fields
        set_listeners() {
            var me = this;
            $(`.${this.datatable.style.scopeClass} .dt-scrollable`).on(
                "click",
                `.btn`,
                function () {
                    // ================================================================================================= //
                    // ==================================== Custom code starts here ==================================== //
                    // ================================================================================================= //
                    // Get the 'Cost Center' field
                    let cost_center_field = me.dialog_manager.dialog.get_field("cost_center");

                    // Set the value of the 'Cost Center' field
                    if (frm.doc.custom_bank_reconciliation_default_cost_center) {
                        console.log("Overriding default value for 'Cost Center'. Setting to " + frm.doc.custom_bank_reconciliation_default_cost_center)
                        cost_center_field.set_value(frm.doc.custom_bank_reconciliation_default_cost_center)
                    }

                    // Change the 'Cost Center' field to show as Mandatory
                    cost_center_field.df.mandatory_depends_on = "eval:doc.action=='Create Voucher'";

                    // Change the 'Cost Center' field to also show for Journal Entries, not only Payment Entries
                    cost_center_field.df.depends_on =
                        "eval:doc.action=='Create Voucher' && (doc.document_type=='Payment Entry' || doc.document_type=='Journal Entry')",
                    cost_center_field.refresh();

                    // Get the 'Second Account' field, and set an onchange function to fetch the default
                    // custom_tax_account, custom_tax_rate_for_bank_recon and custom_cost_center_for_tax_account set on the Account
                    let second_account_field = me.dialog_manager.dialog.get_field("second_account");
                    second_account_field.df.onchange = () => {
                        let secondAccount = me.dialog_manager.dialog.fields_dict.second_account.input.value;
                        frappe.db.get_value('Account', secondAccount, ['custom_tax_account', 'custom_tax_rate_for_bank_recon', 'custom_cost_center_for_tax_account'])
                        .then(r => {
                            let values = r.message;
                            let taxAccountField = me.dialog_manager.dialog.get_field("custom_tax_account");
                            taxAccountField.set_value(values.custom_tax_account)
                            taxAccountField.refresh();
                            let rateField = me.dialog_manager.dialog.get_field("custom_tax_rate_for_bank_recon");
                            rateField.set_value(values.custom_tax_rate_for_bank_recon)
                            rateField.refresh();
                            let costCenterForTaxAcctField = me.dialog_manager.dialog.get_field("custom_cost_center_for_tax_account");
                            costCenterForTaxAcctField.set_value(values.custom_cost_center_for_tax_account || frm.doc.custom_bank_reconciliation_default_cost_center);
                            costCenterForTaxAcctField.refresh();
                        })

                    }
                    second_account_field.refresh();
                    // ================================================================================================= //
                    // ===================================== Custom code ends here ===================================== //
                    // ================================================================================================= //

                    me.dialog_manager.show_dialog(
                        $(this).attr("data-name"),
                        (bank_transaction) => me.update_dt_cards(bank_transaction)
                    );
                    return true;
                }
            );
        } 
    }

    // Same code as "render" function in "Bank Reconciliation Tool", but now the 
    // erpnext.accounts.bank_reconciliation.DataTableManager class has been monkeypatched.
    if (frm.doc.bank_account) {
        frm.bank_reconciliation_data_table_manager = new erpnext.accounts.bank_reconciliation.DataTableManager(
            {
                company: frm.doc.company,
                bank_account: frm.doc.bank_account,
                $reconciliation_tool_dt: frm.get_field(
                    "reconciliation_tool_dt"
                ).$wrapper,
                $no_bank_transactions: frm.get_field(
                    "no_bank_transactions"
                ).$wrapper,
                bank_statement_from_date: frm.doc.bank_statement_from_date,
                bank_statement_to_date: frm.doc.bank_statement_to_date,
                filter_by_reference_date: frm.doc.filter_by_reference_date,
                from_reference_date: frm.doc.from_reference_date,
                to_reference_date: frm.doc.to_reference_date,
                bank_statement_closing_balance:
                    frm.doc.bank_statement_closing_balance,
                cards_manager: frm.cards_manager,
            }
        );
    }
}

// ================================================================================================= //
// ==================================== Custom code starts here ==================================== //
// ================================================================================================= //

// Extend the 'make_reconciliation_tool' function
frappe.ui.form.on(
    'Bank Reconciliation Tool',
    'make_reconciliation_tool',
    function (frm) {
        if (frm.doc.bank_account) {
            fetch_default_cost_center_for_bank_account(frm);
        }
    }
);

// Extend the 'bank_account' function
frappe.ui.form.on(
    'Bank Reconciliation Tool',
    'bank_account',
    function (frm) {
        if (frm.doc.bank_account) {
            fetch_default_cost_center_for_bank_account(frm);
        }
    }
);

// Fetch the custom field for "Bank Reconciliation Default Cost Center" from "Bank Account"
function fetch_default_cost_center_for_bank_account(frm) {
    frappe.db.get_value(
        "Bank Account",
        frm.doc.bank_account,
        "custom_bank_reconciliation_default_cost_center",
        (r) => {
            frm.doc.custom_bank_reconciliation_default_cost_center = r.custom_bank_reconciliation_default_cost_center;
        }
    );
}

// ================================================================================================= //
// ===================================== Custom code ends here ===================================== //
// ================================================================================================= //
