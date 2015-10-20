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
#http://doc.qt.io/qt-5/qtwidgets-itemviews-simpletreemodel-example.html
#http://ftp.ics.uci.edu/pub/centos0/ics-custom-build/BUILD/PyQt-x11-gpl-4.7.2/examples/itemviews/simpletreemodel/simpletreemodel.py

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
        self.view.setModel(self.model2)  # устанавливаем модель для вида
        self.model2.setTable("cases")  # устанавливаем таблицу и селектим из неё всё
        self.model2.select() # вот на этом этапе модель заполняется данными


        self.view.header().moveSection(11,1)
        self.view.header().moveSection(12,2)
        self.view.header().moveSection(13,3)



        self.view.hideColumn(1)
        self.view.hideColumn(6)
        self.view.hideColumn(7)
        self.view.hideColumn(8)
        #self.view.hideColumn(9)
        self.view.header().hideSection(9)
        #


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
        return self.itemData.count()

    def data(self, column):
        try:
            return self.itemData.value(column)
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

class TableToTreeModel2 (QAbstractItemModel):
    """
    Более новый вариант - используем композицию, то есть абстрактная модель
    включает в себя sql табличную модель только для работы с базой данных
    """

    def __init__(self, m, connection):
        QAbstractItemModel.__init__(self, m)

        # попробуем сделать композицию
        self.dbmodel = QSqlTableModel(self, connection)
        self.dbmodel.setEditStrategy(0) # при каждом изменении поля
        #print (self.dbmodel.hasIndex(1,12))


        self.headers=['id',
                      '_buy',
                      'deadline',
                      'made',
                      'significance',
                      'urgency',
                      '_children',
                      '_next',
                      '_parents',
                      '_prev',
                      'season',
                      'short text',
                      'tags',
                      'text']

        self.rootItem = TreeItem (self.headers)

    def setTable(self, tname):
        self.dbmodel.setTable(tname)

    def select(self):
        self.dbmodel.select()
        #здесь должны грузиться данные


        dct = dict () #словарь айди - список строк с данными


        for ind in range (self.dbmodel.rowCount()):
            #dct[int(self.dbmodel.data(self.dbmodel.index(ind,0)))] = [self.dbmodel.data(self.dbmodel.index(ind,j)) for j in range(self.dbmodel.columnCount())]
            dct[int(self.dbmodel.data(self.dbmodel.index(ind,0)))] = self.dbmodel.record(ind)
            self.dbmodel.record(ind).setValue(12, 'sdfsdfsf')


            #dct[int(self.dbmodel.data(self.dbmodel.index(ind,0)))] = ind
            # получается словарь - айдишник к рекорду



        def find_children_and_append (item:TreeItem, dct):
            chlist = eval(item.data(6))
            for ch in chlist:
                tri = TreeItem(dct[ch], item)
                if tri.data(6) != '[]':
                    find_children_and_append(tri,dct)
                item.appendChild(tri)



        #for i in [j for j in dct.values() if j[8]=='[]']:
        for i in [j for j in dct.values() if j.value(8)=='[]']:
            tri = TreeItem(i, self.rootItem)
            find_children_and_append(tri,dct)
            self.rootItem.appendChild(tri)




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
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable |Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
            #return self.dbmodel.headerData(section,orientation,role)


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

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parent()
        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def setData(self, modelIndex, value, int_role=Qt.EditRole):
        """
        Функция вызывается при установке данных
        :param QModelIndex:
        :param QVariant:
        :param int_role:
        :return:
        """
        print ('setdata called', value)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form1 = mainform()
    form1.setWindowTitle("Работа с базами данных в PyQt5")
    form1.show()
    sys.exit(app.exec_())