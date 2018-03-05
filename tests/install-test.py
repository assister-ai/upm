import logging
import os
import shutil

import subprocess

from upm.cli import main
from click.testing import CliRunner
from upm.package.specification import PackageSpecification
from upm.package.specification import load_yaml
from upm.common.const import SPEC_FILE_NAME
from upm.common.const import COMPOSE_FILE
from upm.package.tree import ModuleTree

runner = CliRunner()
examples_dir = os.path.join(os.getcwd(), 'examples')
log = logging.getLogger(__name__)

with runner.isolated_filesystem():
    test_dir_path = os.path.join(os.getcwd(), 'test_dir')
    test_dep1_dir = os.path.join(test_dir_path, 'test-dep1')
    test_dep2_dir = os.path.join(test_dir_path, 'test-dep2')
    test_dep3_dir = os.path.join(test_dir_path, 'test-dep3')
    test_project_dir = os.path.join(test_dir_path, 'test-project')

    shutil.copytree(examples_dir, test_dir_path)

    # Test for 'upm install' without dependency name
    os.chdir(test_project_dir)
    result = runner.invoke(main.main, ['install', test_dep1_dir], catch_exceptions=True)
    specification = PackageSpecification.from_yaml(os.path.join(test_project_dir, SPEC_FILE_NAME))

    assert len(specification.dependencies) == 1 and specification.dependencies[0].name == 'test-dep1'
    compose_file = os.path.join(test_project_dir, COMPOSE_FILE)
    assert os.path.exists(compose_file)
    run = subprocess.run(["docker-compose", "config"])
    assert run.returncode == 0
    dep_tree = ModuleTree.loader(test_project_dir)
    compose_yml = load_yaml(compose_file)
    service_names = []
    for dep in dep_tree.get_level_order_iter():
        service_names.append(dep.get_service_name())

    for k, v in compose_yml['services'].items():
        assert k in service_names
        print("service: %s exist's in compose" % k)

    assert result.exit_code == 0

    # result = subprocess.run(["docker-compose", "ps"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # print(result.stdout)
    # print(result.output)

    # dep_tree = ModuleTree.loader(test_project_dir)
    # print(dep_tree.ascii_art())

