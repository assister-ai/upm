import sys

IS_WINDOWS_PLATFORM = (sys.platform == "win32")
SPEC_FILE_NAME = 'upm.yml'

INITIALIZE_PROMPT_MSG = {
    'name': 'Please enter project name',
    'author': 'Please enter project author',
    'description': 'Please enter project description',
    'version': 'Please enter project version',
    'base': 'Please enter Dockerfile path'
}
