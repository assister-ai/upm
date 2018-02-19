from collections import namedtuple


class Override(namedtuple('Override', 'pkg_name, service')):
    pass


class Dependency(namedtuple('Dependency', 'pkg_name version')):
    pass


class Base(namedtuple('Base', 'image, build, work_dir, user')):
    pass


class Executable(namedtuple('Executable', 'alias, command')):
    pass


class Environment(namedtuple('Environment', 'variable, value')):
    pass


class Service(namedtuple('Service', 'command ports volumes')):
    pass


class Image(namedtuple('Image', 'user name tag registry')):
    pass


class Command(namedtuple('Command', 'path, executable, args')):
    pass


class Volume(namedtuple('Volume', 'src_path, dest_path mode')):
    pass


class PortMap(namedtuple('_PortMap', 'host_ip host_port container protocol')):
    pass



