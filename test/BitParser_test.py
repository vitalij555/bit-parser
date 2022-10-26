import pytest
from unittest.mock import Mock

import sys
# insert at 1, 0 is the script path (or '' in REPL)
if not '../bit-parser' in sys.path:
    sys.path.insert(1, '../bit-parser')

# from BitParser.SubscriberManager import SubscriberManager


class TestExample:
    # def setUpClass():
    #     print("Wow called")
    #
    # def tearDownClass():
    #     print("Wow teardown called...")

    def test_ok(self):
        assert 0 == 0

    def test_ok2(self):
        assert 0 == 0