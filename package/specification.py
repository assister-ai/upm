import os
import logging
import yaml

import click
from collections import namedtuple

from const import SPEC_FILE_NAME

log = logging.getLogger(__name__)


class PackageSpecification(namedtuple('_PackageSpecification',
                                      'working_dir name author version description entrypoints base')):
    def serialize(self):
        file_path = os.path.join(self.working_dir, SPEC_FILE_NAME)
        with open(file_path, 'w') as file:
            yaml.dump(self._asdict(), file, default_flow_style=False, encoding='utf-8', allow_unicode=True)
            file.close()


def init_package_from_prompt(working_dir):
    if package_exists(working_dir):
        print("project already initialized")
    else:
        name, author, version, description, entrypoints, base = get_user_input()

        package = PackageSpecification(working_dir, name, author, version, description, entrypoints, base)
        package.serialize()

        print("project initialized")
        return package


def get_user_input():
    name = click.prompt('Please enter project name', type=str)
    author = click.prompt('Please enter project author', type=str)
    description = click.prompt('Please enter project description', type=str)
    version = click.prompt('Please enter project version', default='0.0.1', type=str)
    base = click.prompt('Please enter Dockerfile path', default='./Dockerfile', type=str)
    entrypoints_flag = True
    entrypoints = {}
    while entrypoints_flag:
        entry_name = click.prompt('Please enter entrypoint name', default='run', type=str)
        entry_command = click.prompt('please enter command', default='npm start', type=str)
        entry_ports = click.prompt('please enter expose ports', default='80,443', type=str)
        entrypoints[entry_name] = {"command": entry_command, "ports": port_mapper(entry_ports)}
        entrypoints_flag = click.prompt('more entrypoint?', default=False, type=bool)
    return name, author, description, version, base, entrypoints


def package_exists(working_dir):
    file_path = os.path.join(working_dir, SPEC_FILE_NAME)
    return os.path.exists(file_path)
