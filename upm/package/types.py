import logging
from collections import namedtuple
import os
import shutil

from common.utils import remove_none_field
from common.const import WORKING_DIR, USER, MODULE_FOLDER
from package.errors import PackageSpecificationSyntax

log = logging.getLogger(__name__)

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


class Daemon(namedtuple('Service', 'command')):
    @classmethod
    def from_dict(cls, service_dict):
        command = service_dict
        return cls(command)

    def to_dict(self):
        return self.command


class Image(namedtuple('Image', 'user name tag registry')):
    pass


class Commit(namedtuple('Commit', 'order command')):
    @classmethod
    def from_dict(cls, commit_map):
        return cls(list(commit_map.keys())[0], list(commit_map.values())[0])

    def to_dict(self):
        dict_temp = dict(self._asdict())
        return {dict_temp['order']: dict_temp['command']}


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
    def parse(cls, volume_dict):
        if not isinstance(volume_dict, str):
            raise PackageSpecificationSyntax('syntax error on Volume')
        vol_array = split_on_colon(volume_dict)
        host_path = vol_array[0]
        container_path = None
        if len(vol_array) > 1:
            container_path = vol_array[1]
        mode = 'rw'
        return cls(host_path, container_path, mode)

    @classmethod
    def default_volumes(cls, parent_src=None):
        volumes = [Volume('./src', '/src', 'rw')]
        if parent_src:
            volumes.append(Volume(parent_src, '/data', 'rw'))
        return volumes

    @classmethod
    def abs_host_path(cls, volume, abs_path):
        def merge(host_path, prefix):
            return os.path.abspath(os.path.join(prefix, host_path))

        return cls(merge(volume.host_path, abs_path), volume.container_path, volume.mode)

    def to_dict(self):
        return "{}:{}".format(self.host_path, self.container_path)


class Port(namedtuple('Port', 'container_port host_port host_ip protocol')):
    @classmethod
    def from_dict(cls, port_dict):
        host_ip = None
        host_port = None
        container_port = None
        protocol = None
        port_as_list = split_on_colon(port_dict)
        if len(port_as_list) == 2:
            host_port = port_as_list[0]
            container_port = port_as_list[1]
        if len(port_as_list) == 1:
            container_port = port_as_list[0]
        # if 'container_port' in port_dict:
        #     container_port = port_dict['container_port']
        # if 'protocol' in port_dict:
        #     protocol = port_dict['protocol']
        return cls(container_port, host_port, host_ip, protocol)

    @classmethod
    def from_ports(cls, container_port, host_port):
        if host_port == 0:
            host_port = None
        return cls(container_port, host_port, None, None)

    def to_dict(self):
        if self.host_port:
            return "{}:{}".format(self.host_port, self.container_port)
        else:
            return str(self.container_port)


def split_on_colon(string):
    return string.split(':')
