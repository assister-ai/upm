import logging
import os
from collections import namedtuple
from pykwalify.core import Core
import yaml

from common.const import SPEC_FILE_NAME
from common.const import PKG_SPECIFICATION_SCHEMA_PATH
from common.utils import remove_none_field
from package.types import Base
from package.types import Volume
from package.types import Daemon
from package.types import Executable
from package.types import Environment
from package.types import Dependency
from package.types import Commit
from package.types import Port
from package.errors import PackageSpecificationError
from package.errors import PackageSpecificationNotFound

log = logging.getLogger(__name__)


class PackageSpecification(
    namedtuple('_PackageSpecification',
               'name author version description daemon executables base environments dependencies volumes commits ports')):
    @classmethod
    def from_dict(cls, pkg_spec_dict):
        log.debug(pkg_spec_dict)
        name = pkg_spec_dict['name']
        log.debug(pkg_spec_dict)
        author = ''
        description = ''
        daemon = None
        executables = None
        dependencies = []
        commits = []
        environments = None
        volumes = None
        ports = None
        if 'author' in pkg_spec_dict:
            author = pkg_spec_dict['author']
        version = pkg_spec_dict['version']
        if 'description' in pkg_spec_dict:
            description = pkg_spec_dict['description']
        base = Base.from_dict(pkg_spec_dict['base'])
        if 'daemon' in pkg_spec_dict:
            daemon = Daemon.from_dict(pkg_spec_dict['daemon'])
        if 'executables' in pkg_spec_dict:
            executables = [Executable.from_dict(executable) for executable in pkg_spec_dict['executables']]
        if 'environments' in pkg_spec_dict:
            environments = [Environment.from_dict(environment) for environment in pkg_spec_dict['environment']]
        if 'dependencies' in pkg_spec_dict:
            dependencies = [Dependency.from_dict(dependency) for dependency in pkg_spec_dict['dependencies']]
        if 'volumes' in pkg_spec_dict:
            volumes = [Volume.parse(volume) for volume in pkg_spec_dict['volumes']]
        if 'commits' in pkg_spec_dict:
            commits = [Commit.from_dict(commit) for commit in pkg_spec_dict['commits']]
        if 'ports' in pkg_spec_dict:
            ports = [Port.from_dict(port) for port in pkg_spec_dict['ports']]

        return cls(name, author, version, description, daemon, executables, base, environments, dependencies, volumes,
                   commits, ports)

    @classmethod
    def from_cli(cls, name, author, version, description, executables_list, base_dict):
        executables = []
        if executables_list and len(executables_list) > 0:
            executables = [Executable.from_dict(executable) for executable in executables_list]
        volumes = Volume.default_volumes()
        return cls(name, author, version, description, None, executables, Base.from_dict(base_dict), None, None,
                   volumes, None, None)

    @classmethod
    def from_yaml(cls, path):
        import package as module
        core_validator = Core(source_file=path,
                              schema_files=[os.path.join(os.path.dirname(module.__file__), PKG_SPECIFICATION_SCHEMA_PATH)])
        core_validator.validate(raise_exception=True)
        sp_dict = load_yaml(path)
        return cls.from_dict(sp_dict)

    def add_dependency_folder(self, location):
        if package_exists(location):
            pkg_spec = load_yaml(os.path.join(location, SPEC_FILE_NAME))
            name = pkg_spec['name']
            self._add_dependency(name, location)
        else:
            raise PackageSpecificationNotFound

    def _add_dependency(self, name, location):
        if not isinstance(self.dependencies, list):
            self.dependencies = []
        for item in self.dependencies:
            if item.name is name:
                self.dependencies.remove(item)
        self.dependencies.append(Dependency(name, location))

    def add_commit(self, command):
        if not isinstance(self.commits, list):
            self.commits = []

        last_commit_index = -1
        for item in self.commits:
            print(item)
            if int(item.order) > last_commit_index:
                last_commit_index = int(item.order)

        self.commits.append(Commit(last_commit_index+1, command))

    @classmethod
    def set_ports(cls, ports, specification):
        return cls(specification.name, specification.author, specification.version, specification.description,
                   specification.daemon, specification.executables, specification.base, specification.environments,
                   specification.dependencies, specification.volumes,
                   specification.commits, ports)

    @classmethod
    def set_daemon(cls, command, specification):
        daemon = Daemon(command)
        return cls(specification.name, specification.author, specification.version, specification.description,
                   daemon, specification.executables, specification.base, specification.environments,
                   specification.dependencies, specification.volumes,
                   specification.commits, specification)

    def to_compose_service(self, service_name):
        service = {}
        if self.base.build:
            service['build'] = self.base.build
        else:
            service['image'] = self.base.image
        service['working_dir'] = self.base.work_dir
        service['user'] = self.base.user

        if self.daemon:
            service['command'] = self.daemon.command

        if self.ports:
            service['ports'] = []
            for port in self.ports:
                if port.host_port:
                    service['ports'].append("{}:{}".format(port.host_port, port.container_port))
                else:
                    service['ports'].append("{}".format(port.container_port))

        if self.volumes:
            service['volumes'] = []
            for volume in self.volumes:
                service['volumes'].append(volume.to_dict())

        service['container_name'] = service_name
        # if self.dependencies:
        #     service['depends_on'] = [get_service_name(dep.name, service_name) for dep in self.dependencies]
        return {service_name: service}

    def to_compose(self, service_name):
        compose_yml = {'version': '3.3', 'services': self.to_compose_service(service_name)}
        return compose_yml

    def to_dict(self):
        result = dict(self._asdict())
        if isinstance(result['base'], Base):
            result['base'] = result['base'].to_dict()

        if isinstance(result['daemon'], Daemon):
            result['daemon'] = result['daemon'].to_dict()

        if isinstance(result['executables'], list):
            temp = []
            for item in result['executables']:
                if isinstance(item, Executable):
                    temp.append(item.to_dict())
                else:
                    temp.append(item)
            result['executables'] = temp

        if isinstance(result['dependencies'], list):
            temp = []
            for item in result['dependencies']:
                if isinstance(item, Dependency):
                    temp.append(item.to_dict())
                else:
                    temp.append(item)
            result['dependencies'] = temp

        if isinstance(result['volumes'], list):
            temp = []
            for item in result['volumes']:
                if isinstance(item, Volume):
                    temp.append(item.to_dict())
                else:
                    temp.append(item)
            result['volumes'] = temp

        if isinstance(result['commits'], list):
            temp = []
            for item in result['commits']:
                if isinstance(item, Commit):
                    temp.append(item.to_dict())
                else:
                    temp.append(item)
            result['commits'] = temp

        if isinstance(result['ports'], list):
            temp = []
            for item in result['ports']:
                if isinstance(item, Port):
                    temp.append(item.to_dict())
                else:
                    temp.append(item)
            result['ports'] = temp

        return result

    def dump(self, path):
        specification_dict = self.to_dict()
        specification_dict = remove_none_field(specification_dict)
        dump_yaml(specification_dict, path, SPEC_FILE_NAME)


def package_exists(working_dir):
    file_path = os.path.join(working_dir, SPEC_FILE_NAME)
    return os.path.exists(file_path)


def get_service_name(pkg_name, parent_name=None):
    if parent_name:
        return '{}_{}'.format(parent_name, pkg_name)
    return pkg_name


def load_yaml(filename):
    try:
        with open(filename, 'r') as fh:
            sp_dict = yaml.safe_load(fh)
            return sp_dict
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise PackageSpecificationError(u"{}: {}".format(error_name, e))


def dump_yaml(specification, package_dir, file_name):
    class MyDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(MyDumper, self).increase_indent(flow, False)

    file_path = os.path.join(package_dir, file_name)
    with open(file_path, 'w') as file:
        yaml.dump(specification, file, Dumper=MyDumper,
                  default_flow_style=False, encoding='utf-8', allow_unicode=True)
        file.close()
