__author__ = 'reiner'


from ui.mainwindow2 import Ui_MainWindow

import sys

import sqlite3

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget

from PyQt5.QtCore import QCoreApplication


from  PyQt5.QtSql import *

class MainWindow2(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Connect up the buttons.
        #self.okButton.clicked.connect(self.accept)
        #self.cancelButton.clicked.connect(self.reject)

        self.pushButton.clicked.connect(self.func_1)
        self.pushButton_2.clicked.connect(self.func_2)
        self.pushButton_3.clicked.connect(self.func_3)
        self.pushButton_4.clicked.connect(self.func_4)

    def func_1(self):
        print (1)
    def func_2(self):
        pass
    def func_3(self):
        pass
    def func_4(self):
        pass



app = QApplication(sys.argv)
window = MainWindow2()

window.show()



sys.exit(app.exec_())