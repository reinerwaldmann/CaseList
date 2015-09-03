from DBStuff import AbstractNode, ItemToBuy, Supplier

__author__ = 'reiner'
import sqlite3


class NoSuchCaseInDBError (Exception):
    pass



class db_serializable ():
    """
    Класс, сериализуемый в базу данных в явном виде,
     то есть в таблицу с полями, в которые пишет свои атрибуты.
     числовые пишет в integer
     всё остальное приводит к string и пишет в текст
     класс достаточно примитивен

     Более продвинутым  в этом плане является sqlalchemy, но для наших целей это перебор

     alpha - пока всем функциям требуется объект, с которым оно и работает
    """


    # Такой пример - сам класс возвращает курсор к базе данных, который можно пользовать в with
    def __enter__(self):
            self.con = sqlite3.connect(self.filename)
            cur = self.con.cursor()
            return cur

    def __exit__(self, exc_type, exc_val, exc_tb):
            self.con.commit()
            self.con.close()

    def __init__(self, filename='cases.sqlite'):
        """
        Класс конфигурируется именем файла и вот ещё словарём типов данных и таблиц
        """
        self.filename = filename
        self.tables = {AbstractNode:'cases', ItemToBuy:'items_to_buy', Supplier:'suppliers'}

        #таблицы по умолчанию


    def get_args_list(self, cls, excluded_attrs=[]):
        """
        Получает список атрибутов у объекта исключая исключаемые
        """
        an = cls () if 'class' in str(type(cls)) else cls

        try:  # пытается вытянуть исключаемые из самого объекта
            excluded_attrs += an.excluded_attrs
        except AttributeError:  # если не удалось, ну и фиг то с ними
            pass

        excluded_attrs += ['_id']
        list_of_attrs = sorted([x for x in list(an.__dict__.keys()) if x not in excluded_attrs])
        list_of_attrs = ['_id']+list_of_attrs
        #  вся эта ересь с айди только по сути для того, чтоб он был первый в списке, так-то у всех объектов должен быть

        return list_of_attrs

    def get_column_list (self, table_or_cls, cur=None):
        """
        Получает список колонок в таблице
        :param table_or_cls это таблица или класс из стандартных
        Внимание: это единственная функция, принимающая на вход cur.
        Ибо иначе может возникнуть ситуация двух вложенных with и cannot operate on closed database
        (внутренний with её закроет)
        """
        table = table_or_cls if type(table_or_cls) is str else self.tables[table_or_cls]

        if cur is None:
            with self as cur:
                ti = cur.execute('PRAGMA table_info({0})'.format (table)).fetchall()
        else:
            ti = cur.execute('PRAGMA table_info({0})'.format (table)).fetchall()

        lss = [k[1] for k in ti]
        return lss


    def _get_table_init_string (self, cls, table=None, excluded_attrs=[]):
        """
        Возвращает строку инициализации таблицы
        """
        an = cls ()  # у полученного объекта все нужные атрибуты

        if not table:
            table = self.tables(cls)

        if table == '':
            table = cls.__name__+'s'

        list_of_attrs = self.get_args_list(cls, excluded_attrs)

        dct = {}
        for attr in list_of_attrs:
            if attr=='_id':
                tp = 'INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL'
            elif type(getattr(an,attr)) is int:
                tp = 'INTEGER'
            elif type(getattr(an,attr)) is float:
                tp = 'REAL'
            else:
                tp = 'TEXT'
            dct[attr] = tp

        creation_string = ",\n".join(['{0} {1}'.format(a, dct[a]) for a in list_of_attrs])
        script_str = """CREATE TABLE IF NOT EXISTS {0} ({1})""".format(table, creation_string)
        return script_str

    def init_table(self, cls, table=None, excluded_attrs=[]):
        """
        Инициализировать таблицу для записи классов
        """
        if not table:
            table = self.tables(cls)

        if table == '':
            table = cls.__name__+'s'

        with self as cur:
            script_str = self._get_table_init_string(cls, table, excluded_attrs)
            cur.execute (script_str)

    def init_all_known_tables (self):
        """
        Работает только если каждый класс знает свои исключаемые атрибуты
        инициализирует таблицы под все известные классы
        """
        for tp, tbl in self.tables:
            self.init_table(tp)



    def insert_to_db (self, obj, table=None):
        """
        Сначала получаем из таблицы названия полей, потом
        всуем в эту таблицу то, что удаётся по этим названием достать из объекта

        Вминание!
        Тут всё очень небезопасно. Во-первых, предполагается, что у таблицы есть поле _id
        Во-вторых, предполагается, что есть такой атрибут у объекта obj
        Также, так как это generic функция, не рассматривается аспект поддержания связей дети-родители и prev-next

        В таблицу записываются только те поля объекта, которые имеются в таблице. Если какого-то нет - будет исключение

        :param obj - записываемый объект
        :param table - таблица, может доставаться из словаря известных

        """

        if not table:
            table = self.tables[type (obj)]

        if table == '':
            table = type (obj).__name__+'s'


        with self as cur:

            collist = self.get_column_list(cur, table)
            if obj._id is None:
                collist.remove('_id')
            else:
                query = 'delete from {0} where _id={1}'.format(table,obj._id)
                cur.execute(query)

            vallist = [str(getattr(obj,x)) for x in collist]
            vallist = ['"'+x+'"' for x in vallist  ] #всё обняли кавычками

            colstr = ','.join(collist)
            valstr = ','.join(vallist)


            scrstr = 'INSERT INTO {0} ({1}) VALUES ({2})'.format (table,colstr,valstr)
            cur.execute(scrstr)

            if obj._id is None:
                obj._id = cur.lastrowid
            return obj


    def get_from_db(self, _id, cls, table=None):
        """
        gets object from database per _id
        :param table - таблица, может доставаться из словаря известных
        :param _id - идентификатор объекта

        При распаковке объекта из таблицы в объект вписываются все атрибуты из колонок таблицы
        то есть, даже те, которых у него не было изначально

        """
        if not table:
            table = self.tables[cls]

        if table == '':
            table = cls.__name__+'s'

        with self as cur:
            query = 'select * from {0} where _id={1}'.format (table, _id)

            cur.execute(query)
            g = cur.fetchone()

            if not g:
                raise NoSuchCaseInDBError

            ooc = cls()

            la = self.get_column_list(table, cur)

            # reconstructing object


            for k,v in zip (la, g):
                setattr(ooc, k, v)


            return ooc



def test():

    filename = 'fn.sqlite'

    dbs = db_serializable(filename)


    an = AbstractNode()
    an._shortText = 'Trololo, hey all'



    #dbs.make_any_query(filename, dbs.insert_to_db, an, 'cases')

    #print (dbs.make_any_query(filename, dbs.get_from_db, 1, AbstractNode, table = 'cases'))


    for i in range (10):
        try:
            print ( dbs.get_from_db(i, AbstractNode, table='cases'))
        except NoSuchCaseInDBError:
            pass





    #print (an)



if __name__ == '__main__':
    test()

# а если инкнудить, то тест не включится

