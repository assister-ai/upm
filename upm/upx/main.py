import click
import logging
import sys
import os

import subprocess
from package.lookup import Lookup
from common.const import IS_WINDOWS_PLATFORM
from common.const import SPEC_FILE_NAME
from package.specification import PackageSpecification
from package.specification import dump_docker_file
from package.tree import ModuleTree

from package.specification import remove_docker_file

log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


@click.command()
@click.option('--debug', is_flag=True)
@click.option('--save', is_flag=True)
@click.option('--daemon', is_flag=True)
@click.argument('command')
@click.argument('args', default=False)
def main(debug, save, daemon, command, args):
    logging.basicConfig(level=logging.INFO)
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    # @TODO find root directory of project instead of working with current dir
    working_dir = os.getcwd()
    lookup = Lookup(working_dir)
    executable = lookup.get(command)
    specification = PackageSpecification.from_yaml(os.path.join(working_dir, SPEC_FILE_NAME))

    # @TODO do appropriate action when executable is None
    if not executable:
        executable = {'name': specification.name, 'command': command, 'alias': None}

    command_array = generate_docker_compose_command(executable['name'], executable['command'], args)
    completed = subprocess.run(command_array)
    # @TODO commit command to image
    # subprocess.run("sudo chown -hR {}:{} ./src".format(os.getuid(), os.getgid()), )
    if completed.returncode == 0:
        fix_owner_ship(os.path.join(working_dir, 'src'))
    # @TODO upx --rollback (remove last commit)
    if save:
        specification = add_commit(executable, args, working_dir)
        dockerfile_content = specification.get_docker_content()
        dump_docker_file(dockerfile_content, working_dir)
        tree = ModuleTree.loader(working_dir)
        root = tree.get_root()
        build = subprocess.run(["docker-compose", "build", root.get_service_name()])
        if build.returncode == 0:
            specification.dump(working_dir)
        else:
            remove_docker_file(working_dir)
            specification = PackageSpecification.from_yaml(os.path.join(working_dir, SPEC_FILE_NAME))
            dockerfile_content = specification.get_docker_content()
            dump_docker_file(dockerfile_content, working_dir)


def generate_docker_compose_command(container_name, command, args=None):
    run = ["docker-compose", "run", "--service-ports", "--rm"]
    if args:
        return run + [container_name] + command.split() + args.split()
    return run + [container_name] + command.split()


def add_args(command, args):
    if not args:
        args = ""
    return ' '.join(command.split() + args.split())


def fix_owner_ship(path):
    if not IS_WINDOWS_PLATFORM:
        new_path = path.join(path, '*')
        fixuid_command = ["sudo", "chown", "-hR", "%s:%s" % (os.geteuid(), os.getegid()), new_path]
        retcode = subprocess.call(fixuid_command)
        return retcode == 0


def add_commit(executable, args, root_path):
    specification = PackageSpecification.from_yaml(os.path.join(root_path, SPEC_FILE_NAME))
    specification.add_commit(add_args(executable['command'], args))
    return specification


if __name__ == '__main__':
    main()
