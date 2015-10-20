__author__ = 'vasilev_is'

import sqlite3
import datetime


def safe_eval (subj, type):
    """
    безопасное конструирование типа из строки
    на входе строка и тип, если строку не удаётся сэвалить,
    вернёт пустой тип
    :param subj:
    :param type:
    :return:
    """
    try:
        return eval(subj)
    except:
        return type()


class AbstractNode ():
    """
    Представление абстрактной ноды, хоть листа, хоть группы
    Разница в листе и в группе лишь в методах
    Ноду можно делать
     - дефолтно
     - из строки базы данных


    """
    def __init__(self, row = None):
        if row is None:
            self._id = None
            self._parents = []
            self._children = []
            self._prev = []
            self._next = []
            self.__buy = []
            self.__deadline = datetime.datetime.today()
            self._season = [6,1,8,31] # сезон, месяц-дата, месяц-дата
            self.__made = False
            self._tags = ''
            self._text = ''
            self._shortText = ''
            self.__urgency = 0
            self.__significance = 0   # доля от итогового результата, контроль 100% не выполняется
        else:
            try:
                self._id = int(row[0])
                self._parents = safe_eval(row[1], list)
                self._children = safe_eval(row[2], list)
                self._prev = safe_eval(row[3], list)
                self._next = safe_eval(row[4], list)
                self.__buy = safe_eval(row[5], list)
                self.__deadline = datetime.date(row[6])
                self._season = safe_eval(row[7], tuple)
                self.__made = safe_eval(row[8], bool)
                self._tags = row[9]
                self._text = row[10]
                self._shortText = row[11]
                self.__urgency = int(row[12])
                self.__significance = int(row[13])   # доля от итогового результата, контроль 100% не выполняется

            except BaseException as e:
                print ('Error while initiation from row due to ', e, row)
                self.__init__()

                # В случае жосского косяка при инициализации, вытряхиваем еррор в консоль,
                # потом производим инициализацию по умолчанию

    def add_child(self, _id):
        self.children.append(_id)

    def remove_child(self, _id):
        self.children.remove(_id)

    def __str__(self):
        rs = ''
        rs += str(self._id)+ '\t'+ self._shortText + '\n'
        rs += 'Дедлайн: {0} Срочнота: {1}  Сезон: {2} '.format(self.__deadline, self.__urgency, self._season) + '\n'
        rs += 'Теги: {0}'.format(self._tags) + '\n'
        rs += 'Предыдущий по алгоритму: {0} Следующий по алгоритму: {1}'.format(self._prev, self._next) + '\n'


            # если есть дети, то есть, это не лист
        for child in self._children:
            ss = child.__str__().split('\n')
            rs += '\t'.join(ss)

        return rs

    def get_made(self):

        # лист или группа - лишь от наличия детей зависит.
        # поведение метода меняется при наличии детей
        if not self.children:
            return self._made

        for child in self.children:
            if not child.get_made():
                return False
            return True


    def make(self):
        if self.children:
            raise Exception ('Cannot make a group')


    def get_deadline(self):
        if not self.children:
            return self.deadline
        # возвращает самый ближний дедлайн, рассматривая свой и детей
        return min (self.deadline, min(x.deadline for x in self.children))


    def get_significance(self):
        if not self.children:
            return self.deadline
        # возвращает максимальную значимость, рассматривая свой и детей
        return max (self.significance, max(x.significance for x in self.children))

    def get_buy_list(self):
        return sum ( [x.get_buy_list() for x in self.children], self.__buy  )


    def get_price(self):
        return sum ( (x.min_price() for x in self.get_buy_list()))

    def get_urgency(self):
        if self._children:
            return max((x.get_urgency() for x in self._children))




class NoSuchCaseInDBError (Exception):
    pass


class DBProcessor():
    def __init__(self, filename_cases, filename_buy=None, filename_suppliers=None):
        self.filename_cases = filename_cases
        self.filename_buy = filename_cases if filename_buy is None else filename_buy
        self.filename_suppliers = filename_cases if filename_suppliers is None else filename_suppliers
        # ещё одна фильтрация None


        self.current_forest = {} # текущий отображаемый лес айди-дерево
     #   self.current_forest_id_list=[]


        self.viewers = [] # подписанные наблюдатели

        self.init_file() # !!! проверить, не затирает ли он таким образом таблицу, если она есть

    def init_file(self):

        con = sqlite3.connect(self.filename)
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS cases (_id INTEGER PRIMARY KEY,
                                                        _parents = TEXT
                                                        _children = TEXT
                                                        _prev = TEXT
                                                        _next = TEXT
                                                        __buy = TEXT
                                                        __deadline = TEXT
                                                        _season = TEXT
                                                        __made = INTEGER
                                                        _tags = TEXT
                                                        _text = TEXT
                                                        _shortText = TEXT
                                                        __urgency = INTEGER
                                                        __significance = INTEGER
                                                        )""")
        con.commit()

        #TODO сюда же относительно покупок и поставщиков тоже включить


    def notify_viewers(self):
        """
        +
        Передать об обновлении
        """
        for viewer in self.viewers:
                viewer.notify (self)

    def load_forest (self, pars=None):
        """
        +
        Загружает лес из базы дел по строке параметров
        """

        con = sqlite3.connect(self.filename_cases)
        cur = con.cursor()

        cur.execute('SELECT * FROM cases {0}'.format('where {0};'.format(pars) if pars and type(pars) is str else ';' ))

        # впихивание натащенного в casesdict
        for row in cur.fetchall():
            self.current_forest[row[0]] = AbstractNode (row)
        con.close()

        self.notify_viewers()

    def load_subtree (self, _id):
        """
        +
        Получает поддерево из базы, обновляя им текущий лес
        """
        def get_subtr(self, _id):
            cur_n = self.get_shit_from_db(_id, AbstractNode)
            self.current_forest[_id] = cur_n
            for ch in cur_n._children:
                get_subtr(self, ch)

        self.current_forest.clear()
        get_subtr(self, _id)

        self.notify_viewers()

    def get_shit_from_db (self, _id, _type, table=None):
        """
        +
        Возвращает хоть что из базы под айдишником
        """

        con = sqlite3.connect(self.filename_cases)
        cur = con.cursor()


        tbl = table if table else {AbstractNode:'cases', ItemToBuy:'items_to_buy', Supplier:'suppliers'}[_type]


        cur.execute('SELECT * FROM {0} where id = `{0}`;'.format(tbl, _id))

        # впихивание натащенного в casesdict

        nd = cur.fetchone()

        con.close()
        if nd is None:
            raise NoSuchCaseInDBError('No such case in cases list')

        return AbstractNode(nd)

    def renew_current_forest(self):
        """
        +
        Обновляет текущий лес из базы
        при использовании кошерных удалителей и добавлятелей какбы не нужен, но в п ервой версии да, нужен
        """
        lst = self.current_forest.keys()
        self.current_forest.clear()

        for id in lst:
            try:
                self.current_forest[id] = self.get_shit_from_db(id, AbstractNode)
                # если не удалось загрузить, то ничего не делать просто
                # так произойдёт штатно, если удалить ноду безопасно и потом попытаться обновить список
                # ведь нода была в том списке
            except:
                pass

        self.notify_viewers()




    def insert_object_to_db (self, object, table, _id=None):
        """
        Вставляет объект в базу данных, возможно, именяя его.
        если изменяет, тогда обновляет тех, кто с ним связан
        если вставляет - тоже
        обновляет автоматом текущее дерево, есл оно содержит вставляемый объект ( в первой версии - безусловно)
        """

        # case 1: no such object yet

        con = sqlite3.connect(self.filename_cases)
        cur = con.cursor()

        ('id',
        'parents',
        'children',
        'prev',
        'next',
        _buy,
        deadline,
        season,
        _made,
        tags,
        text,
        short,
        urgency,
        significance)
        
        

        


        if _id is None:



            #query = (INSERT INTO {0} )

            cur.execute('INSERT INTO users (id, firstName, secondName) VALUES(NULL, "Guido", "van Rossum")')
            con.commit()
            print (cur.lastrowid)



        self.notify_viewers()


    def remove_node (self, id):
        """
        Безопасно удаляет ноду, убивая ссылки на неё
         при нахождении между ссылками, замыкает объекты друг на друга
        """
        self.notify_viewers()

    def link_parent (self, sonid, parentid):
        """

        """
        son = self.get_shit_from_db(sonid, AbstractNode)
        parent= self.get_shit_from_db(parentid, AbstractNode)

        parent._children.append(son._id)
        parent._children = list(set(parent._children)) #на тот случай, если уже была такая запись

        son._parents.append(parent._id)
        son._parents = list(set(son._parents)) #на тот случай, если уже была такая запись

        self.insert_object_to_db(son,sonid)
        self.insert_object_to_db(parent,parentid)

        self.renew_current_forest()

    def unlink_parent (self, sonid, parentid):
        """
        +
        mylist = 3, 2, 2, 1
        mylist = list(set(mylist))
        """
        son = self.get_shit_from_db(sonid, AbstractNode)
        parent= self.get_shit_from_db(parentid, AbstractNode)

        son._parents.remove(parent._id)
        parent._children.remove(son._id)

        self.renew_current_forest()

        self.insert_object_to_db(son,sonid)
        self.insert_object_to_db(parent,parentid)


    def templ_link(self, high, low, highlst, lowlst):
        """
        шаблон для создания связи в двусвязном списке
        """
        son = self.get_shit_from_db(sonid, AbstractNode)
        parent= self.get_shit_from_db(parentid, AbstractNode)

        parent._children.append(son._id)
        parent._children = list(set(parent._children)) #на тот случай, если уже была такая запись

        son._parents.append(parent._id)
        son._parents = list(set(son._parents)) #на тот случай, если уже была такая запись

        self.insert_object_to_db(son,sonid)
        self.insert_object_to_db(parent,parentid)

        self.renew_current_forest()


    def link_prev (self, prev, next):
        """
            +
        """


        self.renew_current_forest()

    def unlink_prev (self, prev, next):
        """
            +
        """


        self.renew_current_forest()

    def add_item_to_buy (self, id_case, item, id_item=None):
        """

        """
        self.renew_current_forest()

    def add_supplier (self, supplier, id_supplier=None):
        """

        """

        self.renew_current_forest()



class ItemToBuy():
    """
    Item to buy
    """


    def __init__(self):
        self.name = ''
        self.comment = ''
        self.suppliers = [] # list of tuple - price, comment, supplier
        self.priority=0
        self.legacy_price=0
        self.legacy_category=''
        self.quantity=0




class Supplier ():
    def __init__(self):
        self.name = ''
        self.address = ''
        self.comment = ''
        self.contacts = ''
        self.gps_coordinates = ''
