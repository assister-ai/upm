import click
import logging
import sys
import os

import subprocess
from package.lookup import Lookup

log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)


@click.command()
@click.option('--debug', default=False, type=bool)
@click.argument('command')
@click.argument('args', default=False)
def main(debug, command, args):
    logging.basicConfig(level=logging.INFO)
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    working_dir = os.getcwd()
    lookup = Lookup(working_dir)
    s = lookup.get(command)
    print(s)
    runner = run_array(s['name'], s['command'], args)
    print(runner)
    if args:
        completed = subprocess.run(runner)
    else:
        completed = subprocess.run(runner)
    # subprocess.run("sudo chown -hR {}:{} ./src".format(os.getuid(), os.getgid()), )
    fix_owner_ship(os.path.join(working_dir, 'src'))
    print(completed.returncode)


def run_array(container_name, command, args):
    run = ["docker-compose", "run"]
    if args:
        return run + [container_name] + command.split() + args.split()
    return run + [container_name] + command.split()


def fix_owner_ship(path):
    sudoPassword = 'feri_it'
    command = 'sudo chown -hR 1000:1000 ./src'
    p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))


if __name__ == '__main__':
    main()
