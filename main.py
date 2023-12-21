from PyQt6.QtWidgets import *
import PyQt6.uic as uic
from PyQt6.QtCore import Qt
import sys
import os
from testObject import Test, PASS, FAIL
import subprocess

class Main(QMainWindow):

    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi("main.ui", self)
        self.setBtns()
        self.tests = list()
        test_header = self.test_table.horizontalHeader()       
        test_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        test_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

    def setBtns(self):
        self.import_tests_btn.clicked.connect(self.import_test)
        self.toggle_all_btn.clicked.connect(self.toggle_all)
        self.show_all_btn.clicked.connect(self.show_all)
        self.show_selected_btn.clicked.connect(self.show_selected)
        self.show_unselected_btn.clicked.connect(self.show_unselected)
        self.run_test_btn.clicked.connect(self.run_tests)
        self.clear_result_btn.clicked.connect(self.clear_result)
        self.export_result_btn.clicked.connect(self.export_result)

    '''
    Import testing data from a selected txt file
    '''
    def import_test(self):
        file_filter = 'TEXT File (*.txt)'
        filename = QFileDialog.getOpenFileName(
            parent = self,
            caption = 'Select a file',
            directory = os.getcwd(),
            filter = file_filter,
        )[0]
        tests = self.get_tests(filename)
        table_widget = self.test_table
        table_widget.setRowCount(len(tests))
        current_row = 0
        if (tests):
            for test in tests:
                self.tests.append(test)
                table_widget.setItem(current_row, 0, QTableWidgetItem(test.case_id + " " + test.test_name))
                table_widget.setItem(current_row, 1, QTableWidgetItem())
                table_widget.item(current_row, 0).setCheckState(Qt.CheckState.Unchecked)
                current_row += 1
            table_widget.itemChanged.connect(self.update_selected)

    '''
    Shows the number of selected tests
    '''
    def update_selected(self):
        selected = 0
        for i in range(self.test_table.rowCount()):
                if (self.test_table.item(i, 0).checkState() == Qt.CheckState.Checked):
                    selected += 1
        self.selected_count_label.setText(f"{selected} test(s) selected")

    '''
    Select/Unselect all tests
    '''
    def toggle_all(self):
        state = Qt.CheckState.Unchecked
        if (any([self.test_table.item(x, 0).checkState() == Qt.CheckState.Unchecked for x in range(len(self.tests))])):
            state = Qt.CheckState.Checked
        for i in range(len(self.tests)):
                self.test_table.item(i, 0).setCheckState(state)

    '''
    Show all tests in the table
    '''
    def show_all(self):
        for i in range(len(self.tests)):
            self.test_table.setRowHidden(i, False)
        
    
    '''
    Show selected tests in the table
    '''
    def show_selected(self):
        for i in range(len(self.tests)):
            item = self.test_table.item(i, 0)
            if (item.checkState() == Qt.CheckState.Checked):
                self.test_table.setRowHidden(i, False)
            else:
                self.test_table.setRowHidden(i, True)

    '''
    Show unselected tests in the table
    '''
    def show_unselected(self):
        for i in range(len(self.tests)):
            item = self.test_table.item(i, 0)
            if (item.checkState() == Qt.CheckState.Unchecked):
                self.test_table.setRowHidden(i, False)
            else:
                self.test_table.setRowHidden(i, True)

    '''
    Run all selected tests
    '''
    def run_tests(self):
        self.clear_result()
        result = list()
        logs = list()
        if (self.tests):
            # Run test and set UI based on result
            for i in range(len(self.tests)):
                if (self.test_table.item(i, 0).checkState() == Qt.CheckState.Checked):
                    test = self.tests[i]
                    response = test.run()
                    logs.append(response['log'])
                    result.append({'test_name': test.test_name, 'result': response['result']})
                    self.setResult(i, response['result'])
            passed_count = 0
            for test_result in result:
                if (test_result['result']):
                    passed_count += 1
            self.passed_label.setText(f'Passed: {passed_count}')
            self.failed_label.setText(f'Failed: {len(result) - passed_count}')
            self.result_log_list.addItems(logs)
            self.logs = logs
        
    '''
    Setting UI for result report
    '''
    def setResult(self, index, result):
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

    '''
    Clear result
    '''
    def clear_result(self):
        self.logs = None
        for i in range(self.test_table.rowCount()):
            self.test_table.item(i, 1).setBackground(Qt.GlobalColor.transparent)
            self.test_table.item(i, 1).setText("")
        self.passed_label.setText(f'Passed:')
        self.failed_label.setText(f'Failed:')
        self.result_log_list.clear()
    
    '''
    Name a file and choose location to store and export as a log file
    '''
    def export_result(self):
        if (not self.logs):
            return
        filename = QFileDialog.getSaveFileName(
            parent = self,
            caption = 'Save file',
            filter = 'LOG files (*.log)',
            directory = os.getcwd()
        )[0]
        with open(filename, "w") as f:
            f.write("======================================================\n")
            for log in self.logs:
                f.write("\n")
                f.write(log)
                f.write("\n")
                f.write("======================================================\n")
            f.write("========================END===========================\n")

    '''
    Parse txt data into test objects
    '''
    def get_tests(self, filename):
        # Retrieve data with pandas framework
        modules = list()
        if (filename):
            tests = list()
            file = open(filename, "r")
            lines = file.readlines()
            readProgram = False
            case_id = ""
            case_name = ""
            program = ""
            for line in lines:
                if ("CaseID" in line):
                    case_id = line.split("=")[1].strip().replace("\n", "")
                elif ("CaseName" in line):
                    if (case_id):
                        case_name = line.split("=")[1].strip().replace("\n", "")
                    else:
                        print("Missing CaseID")
                elif ("start" in line and len(line) == len("start\n")):
                    if (case_id and case_name):
                        readProgram = True
                    else:
                        print("Missing CaseID or Missing CaseName")
                elif ("end" in line and len(line) == len("end\n")):
                    tests.append(Test(case_id, case_name, program))
                    readProgram = False
                    case_id = ""
                    case_name = ""
                    program = ""
                elif(readProgram):
                    if ("import" in line):
                        module = line.split(" ")[1].split(".")[0].replace("\n", "")
                        modules.append(module)
                    program += line
            modules = list(dict.fromkeys(modules))
            self.find_modules(modules)
            return tests
        return None
    
    '''
    Check whether the testing evironment has modules required by the tests
    '''
    def find_modules(self, modules):
        for module in modules:
            if module in sys.modules:
                print("Module is imported.")    
            else:
                print("Module is not imported.")
                # Uncomment the following line to turn on auto module installation feature
                # self.install(module)
    
    '''
    Install a module with name
    '''
    def install(self, module):
        subprocess.check_call(['pip', 'install', module])
        print(f"The module {module} was installed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QListWidget::item { border-bottom: 2px solid gray }")
    win = Main()
    win.setWindowTitle("Automated Testing Tool")
    win.show()
    app.exec()