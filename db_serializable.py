from DBStuff import AbstractNode

__author__ = 'reiner'
import sqlite3


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

    def get_args_list(self, cls, excluded_attrs=[]):
        """
        Получает список атрибутов у объекта исключая исключаемые
        """
        an = cls () if 'class' in str(type(cls)) else cls

        excluded_attrs += ['_id']
        list_of_attrs = sorted([x for x in list(an.__dict__.keys()) if x not in excluded_attrs])
        list_of_attrs = ['_id']+list_of_attrs
        return list_of_attrs

    def get_column_list (self, cur,  table):
        """
        Получает список колонок в таблице
        """

        ti = cur.execute('PRAGMA table_info({0})'.format (table)).fetchall()
        lss = [k[1] for k in ti]
        return lss



    def get_table_init_string (self, cls, table='', excluded_attrs=[]):
        an = cls ()  # у полученного объекта все нужные атрибуты

        if not table:
            table = cls.__name__+'s'

        #excluded_attrs += ['_id']
        #list_of_attrs = sorted([x for x in list(an.__dict__.keys()) if x not in excluded_attrs])

        list_of_attrs = self.get_args_list(cls, excluded_attrs)

        dct = {}
        for attr in list_of_attrs:
            if type(getattr(an,attr)) is int:
                tp = 'INTEGER'
            elif  type(getattr(an,attr)) is float:
                tp = 'REAL'
            else:
                tp = 'TEXT'
            dct[attr] = tp

        creation_string = ",\n".join(['{0} {1}'.format(a, dct[a]) for a in list_of_attrs])
        script_str = """CREATE TABLE IF NOT EXISTS {0} ({1})""".format(table, creation_string)
        return script_str

    def init_table(self, cur, cls, table='', excluded_attrs=[]):
        script_str = self.get_table_init_string(cls, table, excluded_attrs)
        cur.execute (script_str)

    def make_any_query (self, filename, funct, *argc, **argv):
        """
        wrapper around any function connects to DB
        we can make the idea much more elegant, but for now it looks like this
        """
        con = sqlite3.connect(filename)
        cur = con.cursor()
        funct(cur, *argc, **argv)
        con.commit()


    def insert_to_db (self, cur, obj, table, excluded_attrs=[],  _id=None):
        """
        Сначала получаем из таблицы названия полей, потом
        всуем в эту таблицу то, что удаётся по этим названием достать из объекта

        Вминание!
        Тут всё очень небезопасно. Во-первых, предполагается, что у таблицы есть поле _id
        Во-вторых, предполагается, что есть такой атрибут у объекта obj
        Также, так как это generic функция, не рассматривается аспект поддержания связей дети-родители и prev-next

        """
        collist = self.get_column_list(cur, table)
        if obj._id is None:
            collist.remove('_id')
        else:
            query = 'remove from {0} where _id={1}'.format(table,obj._id)
            cur.execute(query)


        vallist = [str(obj.getattr(x)) for x in collist]
        vallist = ['"'+x+'"' for x in vallist  ] #всё обняли кавычками

        colstr = ','.join(collist)
        valstr = ','.join(vallist)


        scrstr = 'INSERT INTO {0} ({1}) VALUES ({2})'.format (table,colstr,valstr)
        cur.execute(scrstr)

        if obj._id is None:
            obj._id = cur.lastrowid
        return obj




        # cur.execute('INSERT INTO users (id, firstName, secondName) VALUES(NULL, "Guido", "van Rossum")')
        # con.commit()
        #print (cur.lastrowid)


    def get_from_db(self, cur, _id=None):
        pass


def test():
    dbs = db_serializable()
    filename = 'fn.sqlite'
    #dbs.make_any_query(filename,dbs.init_table, AbstractNode, table='cases'  )
    an = AbstractNode()

    dbs.make_any_query(filename, dbs.insert_to_db, an, 'cases')





test()