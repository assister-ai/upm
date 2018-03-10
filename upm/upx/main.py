import click
import logging
import sys
import os

import subprocess
from package.lookup import Lookup
from common.const import IS_WINDOWS_PLATFORM
from common.const import SPEC_FILE_NAME
from package.specification import PackageSpecification

log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


@click.command()
@click.option('--debug', default=False, type=bool)
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
        add_commit(executable, args, working_dir)
    if daemon:
        pass


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
        fixuid_command =["sudo", "chown", "-hR", "%s:%s" % (os.geteuid(), os.getegid()), path]
        retcode = subprocess.call(fixuid_command)
        return retcode == 0


def add_commit(executable, args, root_path):
    specification = PackageSpecification.from_yaml(os.path.join(root_path, SPEC_FILE_NAME))
    specification.add_commit(add_args(executable['command'], args))
    specification.dump(root_path)
    return specification


if __name__ == '__main__':
    main()
