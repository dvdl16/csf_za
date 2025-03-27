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

|     | A                          | B          | C                 | D                              | E      | F    | G       |
| --- | -------------------------- | ---------- | ----------------- | ------------------------------ | ------ | ---- | ------- |
| 1   | Balance brought   forward: | 12345      |                   |                                |        |      |         |
| 2   |                            |            |                   |                                |        |      |         |
| 3   | Account                    | Date       | Description       | Reference                      | Amount | Fees | Balance |
| 4   | 123456789                  | 01/01/2025 | Inward EFT Credit | CAPITEC   0103PosSettle 250301 | 123    |      | 444444  |
| 5   |                            |            |                   |                                |        |      |         |
| 6   |                            |            |                   |                                |        |      |         |

### Nedbank

|     | A                     | B               | C    | D     |
| --- | --------------------- | --------------- | ---- | ----- |
| 1   | Statement Enquiry :   |                 |      |       |
| 2   | Account Number :      | 1234567890      |      |       |
| 3   | Account Description : | CURRENT         |      |       |
| 4   | Statement Number :    | 123             |      |       |
| 5   | 01-Jan-25             | BROUGHT FORWARD |      | 10000 |
| 6   | 01-Jan-25             | Payment         | -500 | 9500  |
| 7   | 01-Feb-25             | CARRIED FORWARD |      | 9500  |

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
