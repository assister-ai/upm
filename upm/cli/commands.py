import logging
import os

import click
import subprocess
from common.const import COMPOSE_FILE
from common.const import SPEC_FILE_NAME
from package.errors import PackageSpecificationAlreadyExist
from package.errors import PackageSpecificationNotFound
from package.specification import PackageSpecification
from package.specification import dump_yaml
from package.specification import package_exists
from package.lookup import Lookup
from package.tree import ModuleTree


log = logging.getLogger(__name__)


def initialize_package(working_dir):

    def get_user_input():
        base_types = ['default', 'image', 'file']
        name = click.prompt('Please enter project name', type=str)
        author = click.prompt('Please enter project author', type=str)
        description = click.prompt('Please enter project description', type=str)
        version = click.prompt('Please enter project version', default='0.0.1', type=str)
        base_type = click.prompt('Select your base image?\nfile: Dockerfile\nimage: Docker Image\ndefault: alpine:3.6',
                                 default='default',
                                 type=click.Choice(base_types))

        if str(base_type) == str(base_types[1]):
            image = click.prompt('Please enter DockerImage', default='alpine:3.6', type=str)
            base = {'image': image}
        elif base_type == base_types[2]:
            build = click.prompt('Please enter Dockerfile path', default='./Dockerfile', type=str)
            base = {'build': build}
        elif base_type == base_types[0]:
            image = 'alpine:3.6'
            base = {'image': image}
        else:
            raise ValueError('bad input')

        executable_flag = True
        executables = []
        while executable_flag:
            entry_name = click.prompt('Please enter executable name', default='run', type=str)
            entry_command = click.prompt('please enter command', default='npm start', type=str)
            executable_flag = click.prompt('more entrypoint?', default=False, type=bool)
            executables.append({entry_name: entry_command})

        return name, author, description, version, base, executables

    def from_prompt(package_dir):
        if package_exists(package_dir):
            raise PackageSpecificationAlreadyExist('upm.yml')
        else:
            name, author, description, version, base, executables = get_user_input()
            package = PackageSpecification.from_cli(name, author, version, description, executables, base)
            package.dump(package_dir)
            print("project initialized")
            return package

    from_prompt(working_dir)


def install_package(working_dir, pkg_location=None):
    specification_file = os.path.join(working_dir, SPEC_FILE_NAME)
    if not package_exists(working_dir):
        raise PackageSpecificationNotFound([SPEC_FILE_NAME])

    log.info('loading upm yml')

    package_specification = PackageSpecification.from_yaml(specification_file)
    if pkg_location:
        log.info('try to add dependency to upm')
        package_specification.add_dependency_folder(pkg_location)
        log.info('serializing upm')
        package_specification.dump(working_dir)
        log.info('sucussful')

    log.info('add dependency to upm')

    tree = ModuleTree.installer(working_dir)
    tree.ascii_art()
    dump_yaml(tree.get_compose_dict(), os.path.join(working_dir), COMPOSE_FILE)
    lookup = Lookup(tree.get_module_path())
    lookup.initialize(tree.get_level_order_iter())
    subprocess.run(["docker-compose", "down", "-v"])
    subprocess.run(["docker-compose", "up", "-d", "--build", "--remove-orphans"])
    subprocess.run(["docker-compose", "logs"])






