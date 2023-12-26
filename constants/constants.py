MAIN_UI = "main.ui"
TITLE = "Automation Testing Tool"

IMP_FILTER = "*.txt *.py"
LOG_FILTER = "*.log"

SELECT_FILE_CAPTION = "Select a file"
SAVE_FILE_CAPTION = "Save file"

SEPERATOR = "=====================================\n"
END_SEPERATOR = "=================END=================\n"

TEST_CASE_PY = r"./env/testCase.py"
MODULES_PY = r"./env/modules.py"
PYTHON3 = "python3"
UTF8 = "utf8"
PIP = "pip"
INSTALL = "install"

CASE_ID = "CaseID"
CASE_NAME = "CaseName"
START = "start"
END = "end"

IMPORT = "import"
PRINT = "print"
FLUSH = "sys.stdout.flush()\n"
SYS_IMP = "import sys\n"
MODULES_IMP = "from modules import *\n"
ENV = "env."
PASS = "PASS"
FAIL = "FAIL"

NEXT_LINE = "\n"
EQUAL = "="
SPACE = " "

MODULE_ERR = { "text" : "WARNING: Failed to load modules", "informative_text" : "Missing one or more modules.", "detailed_text" : "Please install the following missing module(s) or fix the path:\n"}
FORMAT_ERR = { "text" : "WARNING: Failed to load test cases", "informative_text" : "Test Cases are in the wrong format", "detailed_text" : "Please check if the test cases are correctly structured"}