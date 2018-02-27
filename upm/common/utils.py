import logging
import os
import shutil

log = logging.getLogger(__name__)


def remove_none_field(specification_dict):
    spec_dict = {}
    for key, value in specification_dict.items():
        if value is not None and len(value) is not 0:
            spec_dict[key] = value
    return spec_dict


def ensure_makedir(file_path):
    if os.path.exists(file_path):
        shutil.rmtree(file_path)
    os.makedirs(file_path)
