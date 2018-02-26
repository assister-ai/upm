import logging
import os
import shutil

from anytree import NodeMixin
from anytree import RenderTree
from anytree import AsciiStyle
from package.specification import PackageSpecification
from package.specification import load_yaml

from common.utils import ensure_makedir
from common.const import MODULE_FOLDER
from common.const import SPEC_FILE_NAME

log = logging.getLogger(__name__)


class ModuleTree:
    def __init__(self, root_path):
        self.root = maker(root_path)
        # print(self.root.children)
        print(RenderTree(self.root, style=AsciiStyle()))


def maker(root_path, parent=None):
    root = ModuleNode(root_path, parent=parent)
    root.install()
    child_list = root.fetch_deps()
    if len(child_list) > 0:
        for child in child_list:
            maker(child, root)
    return root


class ModuleNode(NodeMixin):
    def __init__(self, specification_path, parent=None):
        self.parent = parent
        self.abs_path = os.path.abspath(specification_path)
        self.specification = load_yaml(os.path.join(specification_path, SPEC_FILE_NAME))
        self.abs_module_dir = os.path.join(self.abs_path, MODULE_FOLDER)

    def install(self):
        log.debug(self.abs_module_dir)
        ensure_makedir(self.abs_module_dir)
        self.specification.composer(self.abs_module_dir)

    def fetch_deps(self):
        dependencies = self.specification.dependencies
        module_list = []
        if dependencies and len(dependencies) > 0:
            for dependency in dependencies:
                fetch(dependency.location, dependency.name,self.abs_module_dir)
                new_path = os.path.join(self.abs_module_dir, dependency.name)
                module_list.append(new_path)
        return module_list

    def __repr__(self):
        return '(Node path={} name={})'.format(self.abs_path, self.specification.name)


def fetch(pkg_location, pkg_name, current_location):
    shutil.copytree(pkg_location, os.path.join(current_location, pkg_name))
