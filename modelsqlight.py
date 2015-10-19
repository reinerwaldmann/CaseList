__author__ = 'vasilev_is'

import PyQt5.QtSql as qsq

from PyQt5.QtSql import QSqlTableModel
import PyQt5.QtGui as qg
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QWidget, QApplication, QTableView, QVBoxLayout, QTreeView


class mainform(QWidget):
    """
    Главное окно, оно будет пока и главным классом приложения
    """
    def __init__(self):
        QWidget.__init__(self)
        self.resize(600, 400)
        self.connect()
        #запущаем соединение



    def connect(self):
        con = qsq.QSqlDatabase.addDatabase("QSQLITE", 'Base') #  делаем подключение к БД
        con.setDatabaseName("fn.sqlite") #  устанавливаем имя базы

        if not con.open(): #  если не открылось
            print ("База данных не открылась!")
            print ("-"+con.lastError().text()+"-")
            print (str(con.lastError().type()))
            return

        # cur = qsq.QSqlQuery(con) #  это прямое открытие
        # cur.exec("SELECT * FROM cases")
        # print (cur.lastError().text())

        #self.view = QTableView()  # создаём табличный вид
        self.view = QTreeView()

        self.model2 = TableToTreeModel2(self, con)  # создаём модельку - стандартную для БД, табличную

#http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
        self.view.setModel(self.model2)  # устанавливаем модель для вида

        self.model2.setTable("cases")  # устанавливаем таблицу и селектим из неё всё
        self.model2.select() # вот на этом этапе модель заполняется данными

#        print (self.model2.rowCount()) # возвращает количество строк

        # for i in range (self.model2.rowCount()):
        #     print (self.model2.data ( self.model2.index(i,1) ))


        #self.model2.setFilter('_id>1')  # установка фильтра на селект
        #self.model2.setFilter('')  # и снятие оного



        #print (self.model2.record(0).value('_shortText')) #  так можно получить данные
        #print (self.model2.index(0,0))

#        print (self.model2.data ( self.model2.index(0,0) ))


        self.layout = QVBoxLayout()  # пихаем вид в интерфейс
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        con.close()  # закрываем соединение

#http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/itemviews/simpletreemodel/simpletreemodel.py

class TableToTreeModel2 (QAbstractItemModel):
    """
    Более новый вариант - используем композицию, то есть абстрактная модель
    включает в себя sql табличную модель только для работы с базой данных
    """

    def __init__(self, m, connection):
        QAbstractItemModel.__init__(self, m)

        # попробуем сделать композицию
        self.dbmodel = QSqlTableModel(self, connection)
        self.rootItem = TreeItem (['x' for i in range (14)])



    def setTable(self, tname):
        self.dbmodel.setTable(tname)
    def select(self):
        self.dbmodel.select()
        #здесь должны грузиться данные

        for ind in range (self.dbmodel.rowCount()):
            rec = self.dbmodel.record(ind)
            fnames = [self.dbmodel.record(ind).fieldName(j) for j in range(self.dbmodel.record(ind).count())]
            dlst = [self.dbmodel.record(ind).value(j) for j in range(self.dbmodel.record(ind).count())]

            ii = fnames.index('_parents')
            if dlst[ii]=='[]':
                it = TreeItem (dlst, self.rootItem)
                self.rootItem.appendChild(it)

        print (fnames, dlst)





    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.dbmodel.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        item = index.internalPointer()
        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.dbmodel.headerData(section,orientation,role)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def rowCount(self, parent):

        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()






class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0





class TableToTreeModel (QSqlTableModel):
    structure = []
    def select(self):
        QSqlTableModel.select(self)
        temp = []
        for i in range (self.rowCount()):
            temp.append(self.record(i))

        for t in temp:
            if not eval(str(t.value('_parents'))):
                self.structure.append(TreeItem(t))

    def data(self, index:QModelIndex, int_role=None):
        if not index.isValid():
            return QVariant()


        if int_role != Qt.DisplayRole:
            return QVariant()

        r = index.row()
        c = index.column()

        return self.structure[r].data(c)





         # здесь должна создаваться древовидная структура данных




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form1 = mainform()
    form1.setWindowTitle("Работа с базами данных в PyQt5")
    form1.show()
    sys.exit(app.exec_())