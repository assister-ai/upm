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

from package.networking import NetworkOperatorBase

log = logging.getLogger(__name__)


class ModuleTree:
    def __init__(self, root):
        self.root = root
        self.network_operator = NetworkOperatorBase()

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
        network_structure = self.network_operator.config_network(LevelOrderIter(self.root))
        log.debug("root network config")
        log.debug(self.root.network_configs)
        services = {}
        for node in LevelOrderIter(self.root):
            log.debug("dont fuck with me")
            services.update(node.get_compose_service())
        return {'version': '3.3', 'services': services, 'networks': network_structure.to_compose()}

    def ascii_art(self):
        print(RenderTree(self.root, style=AsciiStyle()))

    def set_network_operator(self, network_operator):
        self.network_operator = network_operator


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
        self.network_configs = NetworkConfigs()

    def install(self):
        ensure_makedir(self.abs_module_dir)

    def add_network_config(self, network_name, name):
        self.network_configs.add_alias(network_name, name)

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

    def get_package_name(self):
        return self.name

    def get_name(self):
        return self.name

    def get_compose_service(self):
        service = self.specification.to_compose_service(self.get_service_name())
        key = list(service.keys())[0]
        value = list(service.values())[0]
        value["networks"] = self.network_configs.to_compose_service_network()
        return {key: value}

    def __repr__(self):
        return '{}'.format(self.name)


class NetworkConfigs:
    def __init__(self):
        self.configs = {}

    def add_network(self, network):
        self.configs[network.name] = network

    def add_alias(self, network_name, alias):
        if network_name not in self.configs.keys():
            self.add_network(NetworkConfig(network_name, [alias]))
        else:
            self.configs[network_name].add_alias(alias)

    def to_compose_service_network(self):
        result = {}
        for config in self.configs.values():
            log.debug(config)
            log.debug(config.to_compose())
            result.update(config.to_compose())
        log.debug(result)
        return result


class NetworkConfig:
    def __init__(self, name, aliases=None):
        if aliases is None:
            aliases = []
        self.name = name
        self.aliases = aliases

    def add_alias(self, alias):
        self.aliases.append(alias)

    def get_aliases(self):
        return self.aliases

    def get_name(self):
        return self.name

    def to_compose(self):
        log.debug(type(self.get_aliases()))
        return {self.get_name(): {'aliases': self.get_aliases()}}
