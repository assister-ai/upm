import logging
import os

log = logging.getLogger(__name__)

def remove_none_field(specification_dict):
    spec_dict = {}
    for key, value in specification_dict.items():
        if value is not None and len(value) is not 0:
            spec_dict[key] = value
    return spec_dict


def ensure_makedir(file_path):
    # directory = os.path.dirname(file_path)
    # log.debug(directory)
    if not os.path.exists(file_path):
        log.debug("why?")
        os.makedirs(file_path)
