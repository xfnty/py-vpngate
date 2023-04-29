[![Code Quality Check](https://github.com/ts-vadim/py-vpngate/actions/workflows/quality-check.yml/badge.svg)](https://github.com/ts-vadim/py-vpngate/actions/workflows/quality-check.yml)

## Useful links
- [Urwid docs](http://urwid.org/tutorial/)

## Installing
**Cloning the repository**
```
git clone https://github.com/ts-vadim/vpngate.git && cd vpngate
```

**Setting up virtual environment**
```
python -m venv .venv
source .venv/bin/activate
```

**Installing dependencies**
- main: `pip install -r requirements/main.txt`
- dev: `pip install -r requirements/dev.txt`

**Running linters on every commit**
1. Install `dev` dependencies with `pip install -r requirements/dev.txt` command.
2. Install pre-commit git hooks:
  - `pre-commit install --hook-type pre-commit`

- *Linters* now will run on every **commit**. Type `pre-commit run -a` to run them manually.
