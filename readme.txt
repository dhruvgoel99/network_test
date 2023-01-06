execute test cases:

pytest
pytest -q test_networks.py
pytest -q test_demo.py

execute markers:

pytest -v -m "cli"
other test cases: (pytest -v -m "not cli")

for checking code score:

pylint test_networks.py
pylint test_demo.py
flake8 test_networks.py
flake8 test_demo.py
pycodestyle test_networks.py
pycodestyle test_demo.py