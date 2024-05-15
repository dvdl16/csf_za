## South Africa Customisations

[ci workflow badge here]
[![codecov](https://codecov.io/gh/dvdl16/csf_za/graph/badge.svg?token=UTL6D9J5J8)](https://codecov.io/gh/dvdl16/csf_za)

Country Specific Functionality for South Africa

This is a Frappe app, intended to be used with ERPNext (version 15).

#### License

MIT


#### Tests

To run unit tests:

```shell
bench --site test_site run-tests --app csf_za --coverage
```

To run UI/integration tests:

The following depencies are required
```shell
sudo apt update
# Dependencies for cypress: https://docs.cypress.io/guides/continuous-integration/introduction#UbuntuDebian
sudo apt-get install libgtk2.0-0 libgtk-3-0 libgbm-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 libxtst6 xauth xvfb

sudo apt-get install chromium
```

```shell
bench --site test_site run-ui-tests csf_za --headless --browser chromium
```

#### Development

We use [pre-commit](https://pre-commit.com/) for linting. First time setup may be required:
```shell
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

#(optional) Run against all the files
pre-commit run --all-files
```

We use [Semgrep](https://semgrep.dev/docs/getting-started/) rules specific to [Frappe Framework](https://github.com/frappe/frappe)
```shell
# Install semgrep
python3 -m pip install semgrep

# Clone the rules repository
git clone --depth 1 https://github.com/frappe/semgrep-rules.git frappe-semgrep-rules

# Run semgrep specifying rules folder as config 
semgrep --config=/workspace/development/frappe-semgrep-rules/rules apps/csf_za
```
