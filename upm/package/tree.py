import logging
import os

from anytree import NodeMixin
from anytree import RenderTree
from anytree import AsciiStyle
from anytree import LevelOrderIter

from common.utils import ensure_makedir
from common.const import MODULE_FOLDER
from common.const import SPEC_FILE_NAME
from package.specification import PackageSpecification

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

    def get_compose_dict(self):
        services = {}
        for node in LevelOrderIter(self.root):
            services.update(node.get_compose_service())
        return {'version': '3.3', 'services': services}

    def ascii_art(self):
        print(RenderTree(self.root, style=AsciiStyle()))


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
            module_loader(child, root)
    return root


class ModuleNode(NodeMixin):
    def __init__(self, specification_path, parent=None):
        self.parent = parent
        self.abs_path = os.path.abspath(specification_path)
        self.specification = PackageSpecification.from_yaml(os.path.join(specification_path, SPEC_FILE_NAME))
        self.abs_module_dir = os.path.join(self.abs_path, MODULE_FOLDER)
        self.name = self.specification.name

    def install(self):
        ensure_makedir(self.abs_module_dir)

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

    def get_service_name(self):
        names = [name.name for name in self.path]
        service_name = '_'.join(names)
        return service_name

    def get_compose_service(self):
        return self.specification.to_compose_service(self.get_service_name())

    def __repr__(self):
        return '{}'.format(self.name)
