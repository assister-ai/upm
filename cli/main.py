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