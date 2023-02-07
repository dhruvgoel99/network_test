1: Create Environment variable for EAPI config file
--> export EAPI_CONF = eapi.conf

2: execute test cases:

--> pytest
--> pytest -q test_networks.py
--> pytest -q test_demo.py

3: execute markers:

--> pytest -v -m "cli"
other test cases: (pytest -v -m "not cli")

4: for checking code score:

--> pylint test_networks.py
--> pylint test_demo.py
--> flake8 test_networks.py
--> flake8 test_demo.py
--> pycodestyle test_networks.py
--> pycodestyle test_demo.py