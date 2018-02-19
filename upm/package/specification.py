import logging
import os
from collections import namedtuple

import yaml
from package.errors import PackageSpecificationError

from common.const import SPEC_FILE_NAME

from upm.package.types import Base
from upm.package.types import Service
from upm.package.types import Executable
from upm.package.types import Environment
from upm.package.types import Dependency


log = logging.getLogger(__name__)


class PackageSpecificationFile(namedtuple('PackageSpecificationFile', 'file_name specification')):
    @classmethod
    def from_file(cls, filename):
        return cls(filename, load_yaml(filename))


class PackageSpecification(
    namedtuple('_PackageSpecification',
               'name author version description service executables base environments dependencies')):
    @classmethod
    def from_dict(cls, pkg_spec_dict):
        name = pkg_spec_dict['name']
        author = ''
        description = ''
        service = None
        executables = None
        dependencies = None
        environments = None
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

        return cls(name, author, version, description, service, executables, base, environments, dependencies)


def load_pkg(pkg_spec_dict):
    pass


def package_exists(working_dir):
    file_path = os.path.join(working_dir, SPEC_FILE_NAME)
    return os.path.exists(file_path)


def load_yaml(filename):
    try:
        with open(filename, 'r') as fh:
            sp_dict = yaml.safe_load(fh)
            return PackageSpecification.from_dict(sp_dict)
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise PackageSpecificationError(u"{}: {}".format(error_name, e))


def dump_yaml(specification_dict, package_dir):
    class MyDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(MyDumper, self).increase_indent(flow, False)

    file_path = os.path.join(package_dir, SPEC_FILE_NAME)
    log.debug(specification_dict)
    with open(file_path, 'w') as file:
        yaml.dump(specification_dict, file, Dumper=MyDumper,
                  default_flow_style=False, encoding='utf-8', allow_unicode=True)
        file.close()
