import os

from tinydb import TinyDB
from tinydb import Query

from common.const import MODULE_FOLDER
from common.const import DB_NAME


class Lookup:
    def __init__(self, root_path):
        self.db_file = os.path.join(root_path, MODULE_FOLDER, DB_NAME)
        self.db = TinyDB(self.db_file)

    def _add(self, name, container_name, executables):
        for executable in executables:
            self.db.insert({'name': name, 'container': container_name, 'alias': executable.alias, 'command': executable.command})

    def initialize(self, node_iter):
        for node in node_iter:
            container_name = node.get_service_name()
            executables = node.get_executables()
            name = node.get_name()
            self._add(name, container_name, executables)

    def get(self, command):
        LP = Query()
        return self.db.get(LP.alias == command)

    def search(self, command):
        LP = Query()
        return self.db.search(LP.alias == command)
