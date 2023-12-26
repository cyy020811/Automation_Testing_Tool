from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtWidgets import *
import PyQt6.uic as uic
import subprocess
import sys
from object.testObject import Test
from constants.constants import *
import pkgutil
import os
from datetime import datetime

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(MAIN_UI, self)
        self.set_btns()
        self.set_header()
        self.tests = list()
        self.process = None
        self.passed_count = 0
        self.failed_count = 0

    """
    Add event listeners to buttons
    """

    def set_btns(self):
        self.import_tests_btn.clicked.connect(self.import_tests)
        self.toggle_all_btn.clicked.connect(self.toggle_all)
        self.show_all_btn.clicked.connect(self.show_all)
        self.show_selected_btn.clicked.connect(self.show_selected)
        self.show_unselected_btn.clicked.connect(self.show_unselected)
        self.run_test_btn.clicked.connect(self.run_tests)
        self.clear_result_btn.clicked.connect(self.clear_result)
        self.export_result_btn.clicked.connect(self.export_result)

    """
    Initialised header
    """

    def set_header(self):
        test_header = self.test_table.horizontalHeader()
        test_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        test_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

    """
    Import testing data from a selected txt file
    """

    def import_tests(self):
        file_filter = IMP_FILTER
        filename = QFileDialog.getOpenFileName(
            parent=self,
            caption=SELECT_FILE_CAPTION,
            directory=os.getcwd(),
            filter=file_filter,
        )[0]
        if (not filename):
            return
        tests = self.get_tests(filename)
        table_widget = self.test_table
        if (tests):
            table_widget.setRowCount(len(tests))
            current_row = 0
            self.tests.clear()
            for test in tests:
                self.tests.append(test)
                table_widget.setItem(
                    current_row,
                    0,
                    QTableWidgetItem(test.case_id + SPACE + test.test_name),
                )
                table_widget.setItem(current_row, 1, QTableWidgetItem())
                table_widget.item(current_row, 0).setCheckState(Qt.CheckState.Unchecked)
                current_row += 1
            table_widget.itemChanged.connect(self.update_selected)
            self.process_list = [None for i in range(len(tests))]

    """
    Shows the number of selected tests
    """

    def update_selected(self):
        selected = 0
        for i in range(self.test_table.rowCount()):
            if (self.test_table.item(i, 0).checkState() == Qt.CheckState.Checked):
                selected += 1
        self.selected_count_label.setText(f"{selected} test(s) selected")

    """
    Select/Unselect all tests
    """

    def toggle_all(self):
        state = Qt.CheckState.Unchecked
        if any(
            [
                self.test_table.item(x, 0).checkState() == Qt.CheckState.Unchecked
                for x in range(len(self.tests))
            ]
        ):
            state = Qt.CheckState.Checked
        for i in range(len(self.tests)):
            self.test_table.item(i, 0).setCheckState(state)

    """
    Show all tests in the table
    """

    def show_all(self):
        for i in range(len(self.tests)):
            self.test_table.setRowHidden(i, False)

    """
    Show selected tests in the table
    """

    def show_selected(self):
        for i in range(len(self.tests)):
            item = self.test_table.item(i, 0)
            if (item.checkState() == Qt.CheckState.Checked):
                self.test_table.setRowHidden(i, False)
            else:
                self.test_table.setRowHidden(i, True)

    """
    Show unselected tests in the table
    """

    def show_unselected(self):
        for i in range(len(self.tests)):
            item = self.test_table.item(i, 0)
            if (item.checkState() == Qt.CheckState.Unchecked):
                self.test_table.setRowHidden(i, False)
            else:
                self.test_table.setRowHidden(i, True)

    """
    Run all selected tests
    """

    def run_tests(self):
        self.clear_result()
        selected_tests = list()
        self.passed_count = 0
        self.failed_count = 0
        if (self.tests):
            for i in range(len(self.tests)):
                if (self.test_table.item(i, 0).checkState() == Qt.CheckState.Checked):
                    selected_tests.append({"test": self.tests[i], "index": i})
            if (selected_tests):
                self.start_process(selected_tests)

    """
    Start a process to execute a test case
    """

    def start_process(self, selected_tests):
        if (self.process is None):
            self.process = QProcess()
            self.testcase_status = False
            test_info = selected_tests.pop(0)
            test = test_info["test"]
            index = test_info["index"]
            self.message(SEPERATOR)
            self.message(f"CaseID: {test.case_id}\nCaseName: {test.test_name}\n")
            print("Executing process")
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.stateChanged.connect(self.handle_state)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.finished.connect(
                lambda: self.process_finished(index, selected_tests)
            )  # Clean up once complete.
            test.build_test()
            self.process.start(PYTHON3, [TEST_CASE_PY])

    """
    Append text to the text browser
    """

    def message(self, text):
        self.result_text_browser.append(text)

    """
    STDOUT processing
    """

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode(UTF8)
        self.message(stdout)
        if (PASS in stdout):
            self.testcase_status = True

    """
    State processing
    """

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: "Not running",
            QProcess.ProcessState.Starting: "Starting",
            QProcess.ProcessState.Running: "Running",
        }
        state_name = states[state]
        print(f"State changed: {state_name}")

    """
    STDERR processing
    """

    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode(UTF8)
        self.message(stderr)
        self.testcase_status = False

    """
    Check if more tests need to be ran and update result
    """

    def process_finished(self, index, selected_tests):
        print("Process finished.")
        self.message(SEPERATOR)
        self.process = None
        self.set_result(index, self.testcase_status)
        if (self.testcase_status):
            self.passed_count += 1
        else:
            self.failed_count += 1
        self.passed_label.setText(f"Passed: {self.passed_count}")
        self.failed_label.setText(f"Failed: {self.failed_count}")
        self.testcase_status = False

        if (selected_tests):
            self.start_process(selected_tests)
        else:
            self.message(END_SEPERATOR)
            os.remove(TEST_CASE_PY)

    """
    Setting UI for result report
    """

    def set_result(self, index, result):
        table_widget = self.test_table
        result_text = FAIL
        bg_color = Qt.GlobalColor.red
        text_color = Qt.GlobalColor.white
        if (result):
            result_text = PASS
            bg_color = Qt.GlobalColor.green
            text_color = Qt.GlobalColor.black
        table_widget.item(index, 1).setText(result_text)
        table_widget.item(index, 1).setBackground(bg_color)
        table_widget.item(index, 1).setForeground(text_color)

    """
    Clear result from UI
    """

    def clear_result(self):
        for i in range(self.test_table.rowCount()):
            self.test_table.item(i, 1).setBackground(Qt.GlobalColor.transparent)
            self.test_table.item(i, 1).setText("")
        self.passed_label.setText("Passed:")
        self.failed_label.setText("Failed:")
        self.result_text_browser.clear()

    """
    Name a file and choose location to store and export as a log file
    """

    def export_result(self):
        if (len(self.result_text_browser.toPlainText())) < 1:
            return
        timestamp = datetime.now().timestamp()
        date_time = datetime.fromtimestamp(timestamp)
        str_date_time = date_time.strftime("%d-%m-%Y, %H:%M:%S")

        with open(f"./log/result-{str_date_time}", "w") as f:
            f.write(self.result_text_browser.toPlainText())

    """
    Parse txt data into test objects
    """

    def get_tests(self, filename):
        if (filename):
            tests = list()
            case_ids = list()
            file = open(filename, "r")
            lines = file.readlines()
            read_program = False

            imports = self.init_modules(lines)
            print(imports)
            if (not imports):
                return None
            
            case_id = ""
            case_name = ""
            program = ""
            start_count = 0
            end_count = 0
            for line in lines:
                if (CASE_ID in line):
                    case_id = line.split(EQUAL)[1].strip().replace(NEXT_LINE, "")
                    case_ids.append(case_id)
                    if (len(case_ids) != len(set(case_ids))):
                        self.warning_gui(FORMAT_ERR)
                        print("Case ID not unique")
                        return None

                elif (CASE_NAME in line):
                    if case_id:
                        case_name = line.split(EQUAL)[1].strip().replace(NEXT_LINE, "")
                    else:
                        self.warning_gui(FORMAT_ERR)
                        print("Missing CaseID")
                        return None

                elif (START in line):
                    if (case_id and case_name):
                        read_program = True
                        program += imports
                        start_count += 1
                    else:
                        self.warning_gui(FORMAT_ERR)
                        print("Missing CaseID or Missing CaseName")
                        return None

                elif (END in line):
                    if (not read_program):
                        self.warning_gui(FORMAT_ERR)
                        print("Exrta end")
                        return None
                    tests.append(Test(case_id, case_name, program))
                    read_program = False
                    case_id = ""
                    case_name = ""
                    program = ""
                    end_count += 1

                if (read_program):
                    if (PRINT in line):
                        spaces = len(line) - len(line.lstrip())
                        line += SPACE * spaces + FLUSH

                    program += line
            file.close()
            if (start_count != end_count):
                self.warning_gui(FORMAT_ERR)
            return tests
        return None

    '''
    Set up environment for test cases
    '''
    def init_modules(self, lines):
        import_lines = [SYS_IMP] + list(filter(lambda line : IMPORT in line, lines))
        modules = list()
        for line in import_lines:
            module = line.split(SPACE)[1].replace(NEXT_LINE, "")
            modules.append(module)
        
        if (self.find_modules(modules)):
            with open(MODULES_PY, "w") as f:
                for line in import_lines:
                    f.write(f"{line}")
            return MODULES_IMP
        return None


    """
    Check whether the testing evironment has modules required by the tests
    """

    def find_modules(self, modules):
        self.missing_modules = list()

        module_found = False
        print(modules)
        for module in modules:
            try:
                loader = pkgutil.find_loader(module)
                if (not loader):
                    self.missing_modules.append(module)
                else: module_found = True
            except:
                self.missing_modules.append(module)

            try:
                loader = pkgutil.find_loader(ENV + module)

                if (not loader and not module_found):
                    self.missing_modules.append(module)
                elif (loader):
                    self.missing_modules.pop()
            except:
                pass

            module_found = False

        print(self.missing_modules)
        if (len(self.missing_modules) > 0):
            self.warning_gui(MODULE_ERR)
            return False
        return True

    """
    Install a module with name
    """

    def install(self, module):
        subprocess.check_call([PIP, INSTALL, module])
        print(f"{module} has been installed")

    '''
    Warning GUI
    '''
    def warning_gui(self, err):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(err["text"])
        msg.setInformativeText(err["informative_text"])
        if (len(self.missing_modules) > 0):
            msg.setDetailedText("Please install the following module(s) or fix import path:\n" + ", ".join(self.missing_modules))
            self.missing_modules.clear()
        else:
            msg.setDetailedText(err["detailed_text"])
        
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main()
    win.setWindowTitle(TITLE)
    win.show()
    app.exec()
