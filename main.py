from pathlib import _Selector

__author__ = 'vasilev_is'
import  sqlite3
import datetime



filename = 'cases.db'

def initFile ():
    global filename
    con = sqlite3.connect('users.db')
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS cases (id INTEGER PRIMARY KEY,
                                                    ifgroup INTEGER,
                                                    self.parents = TEXT
                                                    self.children = TEXT
                                                    self.prev = TEXT
                                                    self.next = TEXT
                                                    self._buy = TEXT
                                                    self.deadline = TEXT
                                                    self.season = TEXT
                                                    self._made = INTEGER
                                                    self.tags = TEXT
                                                    self.text = TEXT
                                                    self.shortText = TEXT
                                                    self.urgency = INTEGER
                                                    self.significance = INTEGER
                                                    )""")
    con.commit()


class AbstractNode ():
    """
    Представление абстрактной ноды, хоть листа, хоть группы
    Разница в листе и в группе лишь в методах
    """
    def __init__(self, row = None):
        if row is None:
            self.id = 0
            self.parents = []
            self.children = []
            self.prev = []
            self.next = []
            self._buy = []
            self.deadline = datetime.today()
            self.season = ((6,1),(8,31)) # сезон, месяц-дата, месяц-дата
            self._made = False
            self.tags = ''
            self.text = ''
            self.shortText = ''
            self.urgency = 0
            self.significance = 0   # доля от итогового результата, контроль 100% не выполняется
        else:
            try:
                self.id = int(row[0])
                self.parents = eval(row[2])
                self.children = eval(row[3])
                self.prev = eval(row[4])
                self.next = eval(row[5])
                self._buy = eval(row[6])
                self.deadline = datetime.date(row[7])
                self.season = eval(row[8])
                self._made = eval(row[9])
                self.tags = row[10]
                self.text = row[10]
                self.shortText = row[12]
                self.urgency = int(row[13])
                self.significance = int(row[14])   # доля от итогового результата, контроль 100% не выполняется

            except BaseException as e:
                print ('Error while initiation from row due to ', e, row)
                self.__init__()

                # В случае жосского косяка при инициализации, вытряхиваем еррор в консоль,
                # потом производим инициализацию по умолчанию


    def get_buy(self):
        # to be implemented in children
        pass

    def get_made(self):
        # to be implemented in children
        pass

    def __str__(self):
        rs = ''
        rs += str(self.id)+ '\t'+ self.shortText + '\n'
        rs += 'Дедлайн: {0} Срочнота: {1}  Сезон: {2} '.format(self.deadline, self.urgency, self.season) + '\n'
        rs += 'Теги: {0}'.format(self.tags) + '\n'
        rs += 'Предыдущий по алгоритму: {0} Следующий по алгоритму: {1}'.format(self.prev, self.next) + '\n'

        if self.children:
            # если есть дети, то есть, это не лист

            for child in sorted(self.children, lambda c: c.significance, reversed = 1):
                ss = child.__str__().split('\n')
                rs += '\t'.join(ss)

        return rs


class Leaf(AbstractNode):
    """
    Представление листа
    """
    def get_buy (self):
        return self._buy

    def get_made(self):
        return self._made

class Group(AbstractNode):
    """
    Представление группы
    """
    def get_buy (self):
        rs = self.buy
        for child in self.children:
            rs.append(child.get_buy)
        return rs

    def get_made(self):
        for child in self.children:
            if not child.made:
                return False
        return True







def insertObjectToBd(node):
    """
    Обновить объект в базе данных
    """

    cur.execute('INSERT INTO users (id, firstName, secondName) VALUES(NULL, "Guido", "van Rossum")')
    con.commit()
    print (cur.lastrowid)

    cur.execute('SELECT * FROM users')
    print (cur.fetchall())
    con.close()


# идея раз: на диске хранится плоская таблица, в которой ссылки на айдишники.
# Когда загружаем структуру в память, делается запрос к БД с фильтром, потом из него делается список объектов,
# из него - словарь айди - объект и вот по этому словарю уже создаётся отображение - делается словарь для отображения,
# потом берётся первя нода без родителей, отображается, потом берутся её дети, отбражаются, (там далее рекурсивно),
# пока не дойдёт до листа. Метод отображения  у ноды один - отобразить себя и детей. Нода без родителей сносится после
#  отображения, а вот прочие ноды не сносятся - ибо ноды могут повторяться в отображении (издержки такие)
# далее вторая нода без родителей и так далее.
#  Потом выводится командная строка  для ввода команд. Так-то можно будет потом в графике в редакторе деревьев любом


# user interaction

def main():
    while (1):
        command = input(':> ').strip()
        parse_str(command)(command)


def parse_str(_str):
    if any(k in _str for k in ['exit', 'e']):
        return lambda x: exit(0)

    if any(k in _str for k in ['select_db', 'sd']):
        return select_db

    if any(k in _str for k in ['select_tree', 'st']):
        return select_tree

    if any(k in _str for k in ['add_node', 'an']):
        return add_node(_str)


    return lambda x: print ('unknown command')

current_tree = {}  # словарь айди - нода

def _add_node_to_db(node):
    pass

def add_node(_str):
    """

    :param _str:
    :return:
    """
    #FIXME переписать с особой жестокостью, потому что тут нет eval. А eval может и None вернуть,
    #FIXME тут придётся преобразовать его в пустой список

    try:
        sl = _str.split(' ')
        id = int (sl[1])

        parents = input('parents []')
        children = input('children []')

        prev = input('prev []')
        _next = input('next []')

        if not children:
            _buy = input('buy []')

        deadline = input('datetime')
        season = input('season ((6,1),(8,31)) сезон, месяц-дата, месяц-дата') #
        tags = input('tags')
        text = input('text')
        shortText = input('shortText')
        urgency = input('urgency - nm')
        significance = input('significance')   # доля от итогового результата, контроль 100% не выполняется

        node = Group() if children else Leaf()

        node.id = id
        node.parents = parents
        node.children = children
        node.prev = prev
        node.next = _next

        if not children:
            node._buy = _buy

        node.deadline = deadline
        node.season = season
        node.tags = tags
        node.text = text
        node.shortText = shortText
        node.urgency = urgency
        node.significance = significance




















    except Exception as e:
        print ('Add Node Failed, due to ', e)






def select_db (_str):
    """
    Команда обновления текущего дерева
    обращает к БД запрос select * from cases where <-и вот в этом месте _str
    :param _str:
    :return:
    """

    global filename
    con = sqlite3.connect(filename)
    cur = con.cursor()

    cur.execute('SELECT * FROM cases {0}'.format('where {0};'.format(_str) if _str else ';' ))

    # впихивание натащенного в casesdict
    for row in cur.fetchall():
        isGrp = bool(row[1])
        if isGrp:
            current_tree[row[0]] = Group (row)
        else:
            current_tree[row[0]] = Leaf (row)


    con.close()
    show_current_tree()




def show_current_tree():
    if not current_tree:
        print ('Current Tree is empty. If it really not, try to select_db')
    for k, v in current_tree.items():
        if not v.parents:
            print (v)
    #  прокручиваем весь словарь текущего дерева, если у ноды нет родителей, то печатать
            # потомков выведет само



def select_tree(_str):
    """
    Очистить область отображения и отобразить только текущее дерево
    :param _str:
    :return:
    """
    if not current_tree:
        print ('Current Tree is empty. If it really not, try to select_db')
    try:
        lstr = _str.split(' ') #распарсили
        id = int(lstr[1])
        print (current_tree[id])

    except Exception as e:
        print ('select_tree commend failed, due to exception ', e)



initFile()
main()