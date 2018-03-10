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

WORKING_DIR = '/src'
SOURCE_DIR = 'src'
USER = 'root'
MODULE_FOLDER = 'universal_modules'
DB_NAME = 'db.json'
COMPOSE_FILE = 'docker-compose.yml'
DOCKER_FILE = 'Dockerfile'
PKG_SPECIFICATION_SCHEMA_PATH = 'validation_schema.yml'
