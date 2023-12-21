from PyQt6.QtWidgets import *

class StdOut(object):
    def __init__(self, widget):
        self.widget = widget
    def write(self, string):
        if (self.widget):
            self.widget.setText(self.widget.text() + string)