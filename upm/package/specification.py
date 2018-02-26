import logging
import os
from collections import namedtuple

import yaml

from common.const import SPEC_FILE_NAME
from common.utils import remove_none_field
from package.types import Base, Volume
from package.types import Service
from package.types import Executable
from package.types import Environment
from package.types import Dependency
from package.errors import PackageSpecificationError
from package.errors import PackageSpecificationNotFound


log = logging.getLogger(__name__)


class PackageSpecificationFile(namedtuple('PackageSpecificationFile', 'file_name specification')):
    @classmethod
    def from_file(cls, filename):
        return cls(filename, load_yaml(filename))


class PackageSpecification(
    namedtuple('_PackageSpecification',
               'name author version description service executables base environments dependencies volumes')):
    @classmethod
    def from_dict(cls, pkg_spec_dict):
        name = pkg_spec_dict['name']
        author = ''
        description = ''
        service = None
        executables = None
        dependencies = []
        environments = None
        volumes = None
        if 'author' in pkg_spec_dict:
            author = pkg_spec_dict['author']
        version = pkg_spec_dict['version']
        if 'description' in pkg_spec_dict:
            description = ''
        base = Base.from_dict(pkg_spec_dict['base'])
        if 'service' in pkg_spec_dict:
            service = Service.from_dict(pkg_spec_dict['service'])
        if 'executables' in pkg_spec_dict:
            executables = [Executable.from_dict(executable) for executable in pkg_spec_dict['executables']]
        if 'environments' in pkg_spec_dict:
            environments = [Environment.from_dict(environment) for environment in pkg_spec_dict['environment']]
        if 'dependencies' in pkg_spec_dict:
            dependencies = [Dependency.from_dict(dependency) for dependency in pkg_spec_dict['dependencies']]
        if 'volumes' in pkg_spec_dict:
            volumes = [Volume.from_dict(volume) for volume in pkg_spec_dict['volumes']]

        return cls(name, author, version, description, service, executables, base, environments, dependencies, volumes)

    @classmethod
    def from_cli(cls, name, author, version, description, executables_list, base_dict):
        log.debug(executables_list)
        if executables_list and len(executables_list) > 0:
            executables = [Executable.from_dict(executable) for executable in executables_list]
        return cls(name, author, version, description, None, executables, Base.from_dict(base_dict), None, None, None)

    def add_dependency_folder(self, location):
        if package_exists(location):
            name = os.path.basename(os.path.normpath(location))
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

    def _compose_repr(self, parent=None):
        service = {}
        if self.base.build:
            service['build'] = self.base.build
        else:
            service['image'] = self.base.image
        service['working_dir'] = self.base.work_dir
        service['user'] = self.base.user

        if self.service:
            service['command'] = self.service.command
            if self.service.ports:
                service['ports'] = {}
                for port in self.service.ports:
                    service['ports'].update({port.host_port: port.container_port})

        if self.volumes:
            service['volumes'] = {}
            for volume in self.volumes:
                service['volumes'].update({volume.src_path: volume.dest_path})
        service_name = get_service_name(self.name, parent)
        service['container_name'] = service_name
        if self.dependencies:
            service['depend_on'] = [get_service_name(dep.name, self.name) for dep in self.dependencies]
        compose_yml = {'version': '3.3', 'services': {service_name: service}}
        return compose_yml

    def composer(self, location, parent=None):
        compose = self._compose_repr(parent)
        dump_yaml(compose, location, 'compose.yml')

    def to_dict(self):
        result = dict(self._asdict())
        log.debug(result)
        if isinstance(result['base'], Base):
            result['base'] = result['base'].to_dict()

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

        return result


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

            return PackageSpecification.from_dict(sp_dict)
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise PackageSpecificationError(u"{}: {}".format(error_name, e))


def dump_upm(specification, package_dir):
    specification_dict = specification.to_dict()
    specification_dict = remove_none_field(specification_dict)
    dump_yaml(specification_dict, package_dir, SPEC_FILE_NAME)


def dump_yaml(specification, package_dir, file_name):
    class MyDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(MyDumper, self).increase_indent(flow, False)

    file_path = os.path.join(package_dir, file_name)
    log.debug(specification)
    with open(file_path, 'w') as file:
        yaml.dump(specification, file, Dumper=MyDumper,
                  default_flow_style=False, encoding='utf-8', allow_unicode=True)
        file.close()
