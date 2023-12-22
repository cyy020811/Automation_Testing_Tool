import random
from io import StringIO
from contextlib import redirect_stdout
import sys
import time
import subprocess
from constants import *

class Test:
    def __init__(self, case_id, test_name, test):
        self.case_id = case_id
        self.test_name = test_name
        self.test = test

    """
    Execute testing script that returns a boolean value and log info
    """

    def build_test(self):
        log = f"CaseID: {self.case_id}\nCaseName: {self.test_name}\n"
        with open(TEST_CASE_PY, "w") as testCase:
            testCase.writelines(self.test)
