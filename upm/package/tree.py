import logging
import os

from anytree import NodeMixin
from anytree import RenderTree
from anytree import AsciiStyle
from anytree import LevelOrderIter


from common.utils import ensure_makedir
from common.const import MODULE_FOLDER
from common.const import SPEC_FILE_NAME
from package.specification import load_yaml
from package.specification import get_service_name

log = logging.getLogger(__name__)


class ModuleTree:
    def __init__(self, root):
        self.root = root

    @classmethod
    def installer(cls, root_path):
        return cls(modules_maker(root_path))

    @classmethod
    def loader(cls, root_path):
        return cls(module_loader(root_path))

    def get_module_path(self):
        return self.root.abs_path

    def get_level_order_iter(self):
        return LevelOrderIter(self.root)

    def __repr__(self):
        log.info(RenderTree(self.root, style=AsciiStyle()))


def modules_maker(root_path, parent=None):
    root = ModuleNode(root_path, parent=parent)
    root.install()
    child_list = root.fetch_dependencies()
    if len(child_list) > 0:
        for child in child_list:
            modules_maker(child, root)
    return root


def module_loader(root_path, parent=None):
    root = ModuleNode(root_path, parent=parent)
    child_list = root.get_installed_dependencies()
    if len(child_list) > 0:
        for child in child_list:
            modules_maker(child, root)
    return root


class ModuleNode(NodeMixin):
    def __init__(self, specification_path, parent=None):
        self.parent = parent
        self.abs_path = os.path.abspath(specification_path)
        self.specification = load_yaml(os.path.join(specification_path, SPEC_FILE_NAME))
        self.abs_module_dir = os.path.join(self.abs_path, MODULE_FOLDER)

    def install(self):
        log.debug(self.abs_module_dir)
        parent_name = None
        if self.parent:
            parent_name = self.parent.specification.name
        ensure_makedir(self.abs_module_dir)
        self.specification.composer(self.abs_module_dir, parent_name)

    def fetch_dependencies(self):
        dependencies = self.specification.dependencies
        module_list = []
        if dependencies and len(dependencies) > 0:
            for dependency in dependencies:
                new_path = dependency.fetch(self.abs_module_dir)
                module_list.append(new_path)
        return module_list

    def get_installed_dependencies(self):
        dependencies = self.specification.dependencies
        module_list = []
        if dependencies and len(dependencies) > 0:
            for dependency in dependencies:
                installed_path = os.path.join(self.abs_module_dir, dependency.name)
                module_list.append(installed_path)
        return module_list

    def get_executables(self):
        return self.specification.executables

    def get_name(self):
        parent_name = None
        if self.parent:
            parent_name = self.parent.specification.name
        name = get_service_name(self.specification.name, parent_name)
        return name

    def __repr__(self):
        return 'name={}'.format(self.abs_path, self.specification.name)


