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

| Balance brought forward: | 122411.10  |                   |                                                    |          |        |           |   |
|--------------------------|------------|-------------------|----------------------------------------------------|----------|--------|-----------|---|
|                          |            |                   |                                                    |          |        |           |   |
| Account                  | Date       | Description       | Reference                                          | Amount   | Fees   | Balance   |   |
| 1051185815               | 31/03/2025 | Debit Order       | CAPITEC   D000001212                               | -1528.49 | -3.00  | 61799.77  |   |
| 1051185815               | 31/03/2025 | Inward EFT Credit | COMPANY X                                          | 19599.08 |        | 81398.85  |   |
| 1051185815               | 31/03/2025 | Inward EFT Credit | CASHFOCUS COMPANY Y                                | 920.77   |        | 82319.62  |   |
| 1051185815               | 31/03/2025 | Inward EFT Credit | CI123456                                           | 78037.40 |        | 160357.02 |   |
| 1051185815               | 31/03/2025 | Month S/Fee       |                                                    |          | -50.00 | 160307.02 |   |
| 1051185815               | 31/03/2025 | Notify Fee        |                                                    |          | -29.40 | 160277.62 |   |
| Total:                   |            |                   |                                                    | 38063.92 | -197.4 | 160277.62 |   |

### Nedbank

| Statement Enquiry :   |                           |         |          |   |
|-----------------------|---------------------------|---------|----------|---|
| Account Number :      | 1234567891                |         |          |   |
| Account Description : | CURRENT                   |         |          |   |
| Statement Number :    | 3000                      |         |          |   |
| 01Mar2025             | ROADCOVER 250301          | -33     | 54676.77 |   |
| 03Mar2025             | loan                      | -1000   | 53676.77 |   |
| 27Mar2025             | VAT 25/02-26/03 = R15.22  |         | 11373.78 |   |
| 27Mar2025             | SERVICE FEE 25/02 - 26/03 | -41.6   | 11332.18 |   |
| 27Mar2025             | MAINTENANCE FEE           | -75     | 11257.18 |   |
| 27Mar2025             | CARRIED FORWARD           |         | 11257.18 |   |
| 27Mar2025             | BROUGHT FORWARD           |         | 11257.18 |   |
| 27Mar2025             | PROVISIONAL STATEMENT     |         |          |   |
| 31Mar2025             | CASHFOCUS DIV             | 9106.98 | 20364.16 |   |

### Standard Bank

|     | A    | B         | C      | D    |                          |                 |     |     |
| --- | ---- | --------- | ------ | ---- | ------------------------ | --------------- | --- | --- |
| 1   | 0    | 123       | BRANCH | 0    |                          | HOGWARTS        | 0   | 0   |
| 2   |      | 987654321 | ACC-NO | 0    |                          |                 |     |     |
| 3   |      | 0         | OPEN   | 1000 | OPEN BALANCE             |                 | 0   | 0   |
| 4   | HIST | 20250101  |        | -100 | AUTOBANK CASH WITHDRAWAL | CHECK GE 465    | 600 | 0   |
| 5   | HIST | 20250101  |        | 100  | IB TRANSFER FROM         | COMPANY X 55555 | 380 | 0   |
| 6   | HIST | 20250101  | ##     | -1   | SERVICE FEE              |                 | 52  | 0   |
| 7   |      | 0         | CLOSE  | 999  | CLOSE BALANCE            |                 | 0   | 0   |

### ABSA

|     | A        | B                  | C      | D       |
| --- | -------- | ------------------ | ------ | ------- |
| 1   | Date     | Description        | Amount | Balance |
| 2   | 20250120 | DIGITAL PAYMENT DT | 100    | 3000    |
| 3   |          |                    |        |         |
