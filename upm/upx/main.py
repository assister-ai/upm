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
@click.argument('command')
@click.argument('args', default=False)
def main(debug, save, command, args):
    logging.basicConfig(level=logging.DEBUG)
    working_dir = os.getcwd()

    if debug:
        logging.basicConfig(level=logging.DEBUG)

    # @TODO upx --rollback (remove last commit)
    if save:
        specification = add_commit(command, args, working_dir)
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
    else:
        # @TODO find root directory of project instead of working with current dir

        lookup = Lookup(working_dir)
        executables = lookup.search(command)

        log.debug(executables)
        log.debug(list(map(lambda x: x['name'], executables)))
        executables_len = len(executables)
        executable = executables[0] if executables_len == 1 else None

        if executables_len > 1:
            executables_names = list(map(lambda x: x['name'], executables))
            select_string = ""
            index = 1
            for name in executables_names[:-1]:
                select_string = select_string + str(index) + " )" + name + " " + "\n" + " "
                index += 1
            select_string = select_string + str(index) + " )" + executables_names[-1]
            msg = "Conflict: packages with this alias :\n {}\n select module to run".format(select_string)
            selected_index = click.prompt(msg, type=click.IntRange(1, len(executables)))
            executable = executables[selected_index - 1]

        if executable is None:
            specification = PackageSpecification.from_yaml(os.path.join(working_dir, SPEC_FILE_NAME))
            log.warning("cant find index it will be run on {}".format(specification.name))
            executable = {'container': specification.name, 'name': specification.name, 'command': command,
                          'alias': None}

        # @TODO do appropriate action when executable is None
        # for executable in executables:

        command_array = generate_docker_compose_command(executable['container'], executable['command'], args)
        completed = subprocess.run(command_array)

        # subprocess.run("sudo chown -hR {}:{} ./src".format(os.getuid(), os.getgid()), )

        if completed.returncode == 0:
            fix_owner_ship(os.path.join(working_dir, 'src'))


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
        fixuid_command = ["sudo", "chown", "-hR", "%s:%s" % (os.geteuid(), os.getegid()), path]
        string_command = " ".join(str(x) for x in fixuid_command)
        log.debug(string_command)
        retcode = subprocess.run(fixuid_command)
        return retcode == 0


def add_commit(command, args, root_path):
    specification = PackageSpecification.from_yaml(os.path.join(root_path, SPEC_FILE_NAME))
    specification.add_commit(add_args(command, args))
    return specification


if __name__ == '__main__':
    main()
