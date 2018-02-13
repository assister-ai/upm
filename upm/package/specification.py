import logging
import os
from collections import namedtuple

import yaml
from package.errors import PackageSpecificationError

from common.const import SPEC_FILE_NAME

log = logging.getLogger(__name__)


class PackageSpecificationFile(namedtuple('PackageSpecificationFile', 'file_name config')):
    @classmethod
    def from_file(cls, filename):
        return cls(filename, load_yaml(filename))


class PackageSpecification(namedtuple('_PackageSpecification',
                                      'name author version description executables base')):
    pass


def package_exists(working_dir):
    file_path = os.path.join(working_dir, SPEC_FILE_NAME)
    return os.path.exists(file_path)


def load_yaml(filename):
    try:
        with open(filename, 'r') as fh:
            return yaml.safe_load(fh)
    except (IOError, yaml.YAMLError) as e:
        error_name = getattr(e, '__module__', '') + '.' + e.__class__.__name__
        raise PackageSpecificationError(u"{}: {}".format(error_name, e))


def dump_yaml(specification_dict, package_dir):
    class MyDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super(MyDumper, self).increase_indent(flow, False)

    file_path = os.path.join(package_dir, SPEC_FILE_NAME)
    log.debug(specification_dict)
    with open(file_path, 'w') as file:
        yaml.dump(specification_dict, file, Dumper=MyDumper,
                  default_flow_style=False, encoding='utf-8', allow_unicode=True)
        file.close()
