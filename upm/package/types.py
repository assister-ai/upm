from collections import namedtuple

from common.const import WORKING_DIR, USER, MODULE_PATH
from package.errors import PackageSpecificationSyntax


class Override(namedtuple('Override', 'pkg_name, service')):
    pass


class Dependency(namedtuple('Dependency', 'name location')):
    @classmethod
    def from_dict(cls, env_dict):
        return cls(list(env_dict.keys())[0], list(env_dict.values())[0])


class Base(namedtuple('Base', 'image build work_dir user')):
    @classmethod
    def from_dict(cls, base_dict):
        key = any_of_build_image(base_dict)
        image = None
        build = None
        work_dir = WORKING_DIR
        user = USER
        if key is 'image':
            image = base_dict[key]
        else:
            build = base_dict[key]
        if 'work_dir' in base_dict:
            work_dir = base_dict['work_dir']
        if 'user' in base_dict:
            user = base_dict['user']
        return cls(image, build, work_dir, user)


def any_of_build_image(base_dict):
    def key_exits(input_dict, key):
        return key in input_dict

    img = key_exits(base_dict, 'image')
    build = key_exits(base_dict, 'build')
    if img != build and img:
        return 'image'
    elif img != build and build:
        return 'build'
    else:
        raise PackageSpecificationSyntax('base')


class Executable(namedtuple('Executable', 'alias command')):
    @classmethod
    def from_dict(cls, executable_map):
        print(executable_map)
        return cls(list(executable_map.keys())[0], list(executable_map.values())[0])


class Environment(namedtuple('Environment', 'variable value')):
    @classmethod
    def from_dict(cls, env_dict):
        return cls(env_dict['variable'], env_dict['value'])


class Service(namedtuple('Service', 'command ports')):
    @classmethod
    def from_dict(cls, service_dict):
        if 'command' not in service_dict:
            raise PackageSpecificationSyntax('command')
        command = service_dict['command']
        ports = None
        if 'ports' in service_dict:
            ports = [Port.from_dict(port) for port in service_dict['ports']]
        return cls(command, ports)


class Image(namedtuple('Image', 'user name tag registry')):
    pass


# class Command(namedtuple('Command', 'executable')):
#    pass
# @classmethod
# def from_dict(cls, command_dict):
#     path = None
#     args = None
#     if 'executable' not in command_dict:
#         raise PackageSpecificationSyntax('command executable')
#     executable = command_dict['executable']
#     if 'args' in command_dict:
#         args = command_dict['args']
#     if 'path' in command_dict:
#         args = command_dict['args']
#     return cls(path, executable, args)


class Volume(namedtuple('Volume', 'src_path dest_path mode')):
    @classmethod
    def from_dict(cls, volume_dict, pkg_name):
        if 'src_path' not in volume_dict:
            raise PackageSpecificationSyntax('volume --> src_path')
        src_path = volume_dict['src_path']
        dest_path = MODULE_PATH + pkg_name + src_path
        mode = 'rw'
        if 'dest_path' in volume_dict:
            dest_path = volume_dict['dest_path']
        if 'mode' in volume_dict:
            mode = volume_dict['mode']
        return cls(src_path, dest_path, mode)


class Port(namedtuple('Port', 'host_ip host_port container_port protocol')):
    @classmethod
    def from_dict(cls, port_dict):
        host_ip = None
        host_port = None
        container_port = None
        protocol = None
        if 'host_ip' in port_dict:
            host_ip = port_dict['host_ip']
        if 'host_port' in port_dict:
            host_port = port_dict['host_port']
        if 'container_port' in port_dict:
            container_port = port_dict['container_port']
        if 'protocol' in port_dict:
            protocol = port_dict['protocol']
        return cls(host_ip, host_port, container_port, protocol)
