import random
from io import StringIO
from contextlib import redirect_stdout
from PyQt6.QtCore import QFileSystemWatcher
import sys

PASS = 'PASS'
FAIL = 'FAIL'

class Test():
    def __init__(self, case_id, test_name, test):
        self.case_id = case_id
        self.test_name = test_name
        self.test = test

    '''
    Execute testing script that returns a boolean value and log info
    '''
    def run(self) -> bool:
        result = dict()
        log = f'CaseID: {self.case_id}\nCaseName: {self.test_name}\n'
        try:
            exec(self.test, globals(), result)
        except Exception as e:
            log += str(e)

        return { 'result' : random.random() < 0.5, "log" : log }

        #Uncomment the following line to return actual result
        # return { 'result' : result['result'] < 0.5, "log" : log }