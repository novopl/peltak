# pylint: disable=missing-docstring
from unittest.mock import Mock, call, mock_open, patch

from peltak.core import conf, util


test_yaml = '''
version: '0.1'

src_dir: src
src_path: 'src/peltak'
build_dir: .build
version_file: 'src/peltak/__init__.py'

commands:
  - peltak.cli.git
  - peltak.cli.lint
  - peltak.cli.test
  - peltak.cli.version

docker:
  registry: docker.novocode.net

lint:
  paths:
    - src/peltak

docs:
  reference:
    - src/peltak

test:
  types:
    default:
      paths:
        - src/peltak
        - test/unit
'''
test_config = util.yaml_load(test_yaml)


@patch('peltak.core.conf.open', mock_open(read_data=test_yaml))
@patch('peltak.core.conf.py_import', Mock())
def test_properly_loads_all_config_variables():
    values = conf._load_from_file('pelconf.yaml')

    assert values == test_config


@patch('peltak.core.conf.open', mock_open(read_data=test_yaml))
@patch('peltak.core.conf.py_import')
def test_imports_commands(p_import):
    values = conf._load_from_file('pelconf.yaml')

    p_import.has_calls([
        call('peltak.cli.git'),
        call('peltak.cli.lint'),
        call('peltak.cli.test'),
        call('peltak.cli.version'),
    ])
    assert values == test_config
