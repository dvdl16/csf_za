context('Bank Reconciliation Tool', () => {
    before(() => {
        cy.login('Administrator', 'admin');
        cy.visit('/desk');
    });

    it('fetches defaults from account master when creating a journal entry', () => {
        const expense_account_name = "Telephone Expenses - SP";
        const custom_tax_account = "VAT - SP";
        const custom_tax_rate_for_bank_recon = 15;
        const custom_cost_center_for_tax_account = "Main - SP"

        // Prepare the data
        cy.call("csf_za.tests.ui_test_helpers.setup_data_for_bank_reconciliation_tool_customisation_tests", {
            expense_account_name: expense_account_name,
            custom_tax_account: custom_tax_account,
            custom_tax_rate_for_bank_recon: custom_tax_rate_for_bank_recon,
            custom_cost_center_for_tax_account: custom_cost_center_for_tax_account
        }).then(() => {

            // Navigate to the bank reconciliation tool page
            cy.visit("/app/bank-reconciliation-tool/Bank Reconciliation Tool");

            // Select the company filter field and fill in the company name
            cy.get_field("company", "Link").clear();
            cy.fill_field("company", "Sun Power Pty Ltd", "Link").focus().blur();

            // Select the bank account filter field and fill in the bank account name
            cy.get_field("bank_account", "Link");
            cy.fill_field("bank_account", "Checking Account - Test Bank", "Link").focus().blur();

            // Select the bank statement start date and set the date value
            cy.get_field("bank_statement_from_date", "Date");
            cy.fill_field("bank_statement_from_date", "01-01-2020", "Date").blur();
            
            // Select the bank statement end date and set the date value
            cy.get_field("bank_statement_to_date", "Date");
            cy.fill_field("bank_statement_to_date", "01-01-2040", "Date").blur();

            // Click the "Get Unreconciled Entries" button
            cy.get(`.btn-primary[data-label="${encodeURIComponent("Get Unreconciled Entries")}"]`).click();

            // Click on the first row's primary button in the datatable
            cy.get('.dt-row-0 .btn-primary').click();

            // Select the action field and set it to "Create Voucher"
            cy.get_field("action", "Select");
            cy.fill_field("action", "Create Voucher", "Select")

            // Select the document type field and set it to "Payment Entry"
            cy.get_field("document_type", "Select");
            cy.fill_field("document_type", "Payment Entry", "Select")

            // Check if the Tax Details section is hidden when the document type is "Payment Entry"
            cy.get(".section-head").contains("Tax Details").parent().should("have.class", "hide-control");

            // Change the document type to "Journal Entry"
            cy.get_field("document_type", "Select");
            cy.fill_field("document_type", "Journal Entry", "Select")

            // Check if the Tax Details section is visible when the document type is "Journal Entry"
            cy.get(".section-head").contains("Tax Details").parent().should("not.have.class", "hidden");

            // Select the second account field and fill it with the expense_account_name value
            cy.get_field("second_account", "Link");
            cy.fill_field("second_account", expense_account_name, "Link").focus().blur().wait(500);

            cy.get(`[data-fieldname="custom_tax_rate_for_bank_recon"]`).first().scrollIntoView();

            // Check if the value of the 'custom_tax_account' field in the current dialog is equal to the expected 'custom_tax_account' value
            cy.window().its("cur_dialog.fields_dict.custom_tax_account.value").should("be.equal", custom_tax_account)

            // Check if the value of the 'custom_tax_rate_for_bank_recon' field in the current dialog is equal to the expected 'custom_tax_rate_for_bank_recon' value
            cy.window().its("cur_dialog.fields_dict.custom_tax_rate_for_bank_recon.value").should("be.equal", custom_tax_rate_for_bank_recon)

            // Check if the value of the 'custom_cost_center_for_tax_account' field in the current dialog is equal to the expected 'custom_cost_center_for_tax_account' value
            cy.window().its("cur_dialog.fields_dict.custom_cost_center_for_tax_account.value").should("be.equal", custom_cost_center_for_tax_account)
        });
    });
});

