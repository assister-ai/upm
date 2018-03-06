import logging
import os

from upm.cli import main
from click.testing import CliRunner
from upm.common.const import SPEC_FILE_NAME
from upm.package.specification import PackageSpecification

runner = CliRunner()
with runner.isolated_filesystem():
    result = runner.invoke(main.main, ['init'],
                           input='test project\nferi,mehdi\ntesting for upm\n0.0.1\n\nrun\nnpm start\nn')
    assert os.path.exists(SPEC_FILE_NAME)
    specification = PackageSpecification.from_yaml(os.path.join(os.getcwd(), SPEC_FILE_NAME))
    assert specification.name == 'test project'
    assert specification.author == 'feri,mehdi'
    assert specification.description == 'testing for upm'
    assert specification.version == '0.0.1'

    executable = specification.executables[0]
    assert executable.alias == 'run'
    assert executable.command == 'npm start'

    volume = specification.volumes[0]
    assert volume.host_path == './src'
    assert volume.container_path == '/src'
    assert volume.mode == 'rw'

    logging.info('All tests passed')
