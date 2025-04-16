# Bank Statement Import for local banks

🚧 This documentation is still under construction 🚧
- [x] Create page for feautre
- [ ] Add all steps with screenshots


## Setup

On the relevant **Bank** records, choose the correct South African Bank:

![Bank Template on Bank doctype](images/bank-template.png)

## Bank Statement Import

When attaching a `.csv` file on a **Bank Statement Import**, the parsing would be performed according to the *Bank Statement Template* of the linked **Bank**

## Template Definitions

These are the established `.csv` formats

### First National Bank

|     | A                             | B           | C      | D                      | E                      | F        | G             | H   |
| --- | ----------------------------- | ----------- | ------ | ---------------------- | ---------------------- | -------- | ------------- | --- |
| 1   | ACCOUNT TRANSACTION HISTORY   |             |        |                        |                        |          |               |     |
| 2   | FOR ACCOUNT NUMBER 1234567890 |             |        |                        |                        |          |               |     |
| 3   | Date                          | SERVICE FEE | Amount | DESCRIPTION            | REFERENCE              | Balance  | CHEQUE NUMBER |     |
| 4   | 2025/01/01                    | 0           | 750    | FNB APP PAYMENT FROM X | FNB APP PAYMENT FROM X | -1234567 | 0             |     |
| 5   |                               |             |        |                        |                        |          |               |     |
| 6   |                               |             |        |                        |                        |          |               |     |

### Bank Zero

|     | A    | B   | C    | D    | E             | F             | G   | H      | I       | J               |
| --- | ---- | --- | ---- | ---- | ------------- | ------------- | --- | ------ | ------- | --------------- |
| 1   | Date | Day | Time | Type | Description 1 | Description 2 | Fee | Amount | Balance | Has Attachments |
| 2   |      |     |      |      |               |               |     |        |         |                 |
| 3   |      |     |      |      |               |               |     |        |         |                 |

### Capitec

|    | A                        | B          | C                 | D                                                  | E        | F      | G         | H |
|----|--------------------------|------------|-------------------|----------------------------------------------------|----------|--------|-----------|---|
| 1  | Balance brought forward: | 122411.10  |                   |                                                    |          |        |           |   |
| 2  |                          |            |                   |                                                    |          |        |           |   |
| 3  | Account                  | Date       | Description       | Reference                                          | Amount   | Fees   | Balance   |   |
| 4  | 1051185815               | 31/03/2025 | Debit Order       | CAPITEC   D000001212                               | -1528.49 | -3.00  | 61799.77  |   |
| 5  | 1051185815               | 31/03/2025 | Inward EFT Credit | COMPANY X                                          | 19599.08 |        | 81398.85  |   |
| 6  | 1051185815               | 31/03/2025 | Inward EFT Credit | CASHFOCUS COMPANY Y                                | 920.77   |        | 82319.62  |   |
| 7  | 1051185815               | 31/03/2025 | Inward EFT Credit | CI123456                                           | 78037.40 |        | 160357.02 |   |
| 8  | 1051185815               | 31/03/2025 | Month S/Fee       |                                                    |          | -50.00 | 160307.02 |   |
| 9  | 1051185815               | 31/03/2025 | Notify Fee        |                                                    |          | -29.40 | 160277.62 |   |
| 10 | Total:                   |            |                   |                                                    | 38063.92 | -197.4 | 160277.62 |   |

### Nedbank

|    | A                     | B                         | C       | D        | E |
|----|-----------------------|---------------------------|---------|----------|---|
| 1  | Statement Enquiry :   |                           |         |          |   |
| 2  | Account Number :      | 1234567891                |         |          |   |
| 3  | Account Description : | CURRENT                   |         |          |   |
| 4  | Statement Number :    | 3000                      |         |          |   |
| 5  | 01Mar2025             | ROADCOVER 250301          | -33     | 54676.77 |   |
| 6  | 03Mar2025             | loan                      | -1000   | 53676.77 |   |
| 7  | 27Mar2025             | VAT 25/02-26/03 = R15.22  |         | 11373.78 |   |
| 8  | 27Mar2025             | SERVICE FEE 25/02 - 26/03 | -41.6   | 11332.18 |   |
| 9  | 27Mar2025             | MAINTENANCE FEE           | -75     | 11257.18 |   |
| 10 | 27Mar2025             | CARRIED FORWARD           |         | 11257.18 |   |
| 11 | 27Mar2025             | BROUGHT FORWARD           |         | 11257.18 |   |
| 12 | 27Mar2025             | PROVISIONAL STATEMENT     |         |          |   |
| 13 | 31Mar2025             | CASHFOCUS DIV             | 9106.98 | 20364.16 |   |

### Standard Bank

|    | A                    | B                        | C                | D                                                                 | E         | F          | G    | H                              | I                  | J |
|----|----------------------|--------------------------|------------------|-------------------------------------------------------------------|-----------|------------|------|--------------------------------|--------------------|---|
| 1  | Statement of Account |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 2  |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 3  | Account Name:        | MY COMPANY PTY LTD       |                  |                                                                   |           |            |      |                                |                    |   |
| 4  |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 5  | Account No:          | 12345678 - SBZAZAJJ      |                  |                                                                   |           |            |      |                                |                    |   |
| 6  |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 7  | A/C Type:            | ORD CURRENT ACCOUNT      |                  |                                                                   |           |            |      |                                |                    |   |
| 8  |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 9  | BIC Code:            | SBZAZAJJ                 |                  |                                                                   |           |            |      |                                |                    |   |
| 10 |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 11 | Bank Name:           | STANDARD BANK OF SA LTD  |                  |                                                                   |           |            |      |                                |                    |   |
| 12 |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 13 | Currency:            | ZAR - SOUTH AFRICAN RAND |                  |                                                                   |           |            |      |                                |                    |   |
| 14 |                      |                          |                  |                                                                   |           |            |      |                                |                    |   |
| 15 | Date                 | Value Date               | Statement Number | Description                                                       | Amount    | Balance    | Type | Originator Reference           | Customer Reference |   |
| 16 | 2025/02/04           | 2025/02/04               | 0249             | OPEN BALANCE 0402 000000000000000                                 |           | +509910.25 |      | OPEN BALANCE                   |                    |   |
| 17 | 2025/04/02           | 2025/04/02               | 0250             | IB PAYMENT TO ABSA HOME 12345678 ABSA HOME 2 0204 000000000000111 | -7000.00  | +138985.31 | TRF  | ABSA HOME 12345678 ABSA HOME 2 |                    |   |
| 18 | 2025/04/02           | 2025/04/02               | 0250             | ELECTRONIC BANKING PAYMENT TO 12345 REFERENCE 01 000000000000509  | -22046.86 | +116938.45 | TRF  | REFERENCE 01                   |                    |   |
| 19 | 2025/04/02           | 2025/04/02               | 0250             | ELECTRONIC BANKING PAYMENT TO 12345 REFERENCE 01 000000000000509  | -35448.75 | +81489.70  | TRF  | REFERENCE 01                   |                    |   |
| 20 | 2025/04/02           | 2025/04/02               | 0250             | IB PAYMENT TO SB FLEET MAN 0204 000000000000111                   | -35826.69 | +45663.01  | TRF  | SB FLEET MAN                   |                    |   |
| 21 | 2025/04/02           | 2025/04/02               | 0250             | CLOSE BALANCE 0204 000000000000000                                |           | +45663.01  | TRF  | CLOSE BALANCE                  |                    |   |

### ABSA

|     | A        | B                  | C      | D       |
| --- | -------- | ------------------ | ------ | ------- |
| 1   | Date     | Description        | Amount | Balance |
| 2   | 20250120 | DIGITAL PAYMENT DT | 100    | 3000    |
| 3   |          |                    |        |         |
