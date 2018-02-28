from collections import namedtuple
import os
import shutil

from common.utils import remove_none_field
from common.const import WORKING_DIR, USER, MODULE_FOLDER
from package.errors import PackageSpecificationSyntax


class Override(namedtuple('Override', 'pkg_name, service')):
    pass


class Dependency(namedtuple('Dependency', 'name location')):
    @classmethod
    def from_dict(cls, env_dict):
        return cls(list(env_dict.keys())[0], list(env_dict.values())[0])

    def to_dict(self):
        dict_temp = dict(self._asdict())
        return {dict_temp['name']: dict_temp['location']}

    def fetch(self, target):
        dest = os.path.join(target, self.name)
        shutil.copytree(self.location, dest)
        return dest


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

    def to_dict(self):
        return remove_none_field(dict(self._asdict()))


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
        return cls(list(executable_map.keys())[0], list(executable_map.values())[0])

    def to_dict(self):
        dict_temp = dict(self._asdict())
        return {dict_temp['alias']: dict_temp['command']}


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


class Volume(namedtuple('Volume', 'host_path container_path mode')):
    @classmethod
    def from_dict(cls, volume_dict):
        if not isinstance(volume_dict, dict):
            raise PackageSpecificationSyntax('volume --> src_path')
        host_path = list(volume_dict.keys())[0]
        container_path = list(volume_dict.values())[0]
        mode = 'rw'
        return cls(host_path, container_path, mode)

    @classmethod
    def default_volumes(cls, parent_src=None):
        volumes = [Volume('./src', '/src', 'rw')]
        if parent_src:
            volumes.append(Volume(parent_src, '/data', 'rw'))
        return volumes

    def to_dict(self):
        return "{}:{}".format(self.host_path, self.container_path)


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
