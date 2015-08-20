__author__ = 'vasilev_is'


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
            self._id = 0
            self._parents = []
            self._children = []
            self._prev = []
            self._next = []
            self.__buy = []
            self.__deadline = datetime.today()
            self._season = ((6,1),(8,31)) # сезон, месяц-дата, месяц-дата
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





