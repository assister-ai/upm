from inspect import getdoc
from const import IS_WINDOWS_PLATFORM

from compose.cli.docopt_command import DocoptDispatcher
from compose.cli.docopt_command import NoSuchCommand
from compose.cli.docopt_command import get_handler


if not IS_WINDOWS_PLATFORM:
    from dockerpty.pty import PseudoTerminal, RunOperation, ExecOperation


class TopLevelCommand(object):
    """ universal package manager for micro-services.

    Usage:
      upm [-f <arg>...] [options] [COMMAND] [ARGS...]
      upm -h|--help

    Options:
      -f, --file FILE             Specify an alternate upm package (default: upm.yml)
      --verbose                   Show more output
      -v, --version               Print version and exit

    Commands:
      init              Generate upm.yml interactively.
      install           get, install and start dependency. add new dependencies.

    """

    def init(self, options):
        """
        initialize package for new or existing source code.
        Usage: init [options].
        """
        pass

    def install(self, options):
        """
        install dependency in package description. create, start dependency service containers.
        Usage: install [<pkg_name>].
        """
        pass

    @classmethod
    def help(cls, options):
        """
        Get help on a command.

        Usage: help [COMMAND]
        """
        if options['COMMAND']:
            subject = get_handler(cls, options['COMMAND'])
        else:
            subject = cls

        print(getdoc(subject))
