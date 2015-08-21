"""
Different commands to be described in this file
"""

__author__ = 'reiner'
import DBStuff



class AbstractCommand():
    def execute(self):
        raise NotImplementedError()

    def undo(self):
        raise NotImplementedError()

    def name(self):
        raise NotImplementedError()

class AddNodeCommand(AbstractCommand):

    def __init__(self, dbp, node):
        self.dbp = dbp
        self.node = node

        self.id_added = None # присваивает тогда, кода вставит

    def execute(self):
        pass


    def undo(self):
        pass




