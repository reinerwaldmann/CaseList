__author__ = 'vasilev_is'


import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget

from PyQt5.QtCore import QCoreApplication



from ui.mainwindow import Ui_MainWindow

#mw = Ui_MainWindow ()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.executeCommand)

        # Connect up the buttons.
        #self.okButton.clicked.connect(self.accept)
        #self.cancelButton.clicked.connect(self.reject)


    def executeCommand(self):
        self.plainTextEdit.appendPlainText('LOL ЛОЛ')

app = QApplication(sys.argv)
window = MainWindow()

window.show()



sys.exit(app.exec_())

#sys.exit(app.exec_())



# from tkinter import *
# import ttk
#
# root = Tk()
#
# tree = ttk.Treeview(root)
#
# tree["columns"]=("one","two")
# tree.column("one", width=100 )
# tree.column("two", width=100)
# tree.heading("one", text="coulmn A")
# tree.heading("two", text="column B")
#
# tree.insert("" , 0,    text="Line 1", values=("1A","1b"))
#
# id2 = tree.insert("", 1, "dir2", text="Dir 2")
# tree.insert(id2, "end", "dir 2", text="sub dir 2", values=("2A","2B"))
#
# ##alternatively:
# tree.insert("", 3, "dir3", text="Dir 3")
# tree.insert("dir3", 3, text=" sub dir 3",values=("3A"," 3B"))
#
# tree.pack()
# root.mainloop()