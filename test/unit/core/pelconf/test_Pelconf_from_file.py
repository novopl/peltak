# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import patch, mock_open, Mock, call

# local imports
from peltak.core import conf
from peltak.core import util


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


@patch('peltak.core.pelconf.open', mock_open(read_data=test_yaml))
@patch('peltak.core.pelconf._import', Mock())
def test_properly_loads_all_config_variables():
    conf.from_file('pelconf.yaml')

    assert conf.values == test_config


@patch('peltak.core.pelconf.open', mock_open(read_data=test_yaml))
@patch('peltak.core.pelconf._import')
def test_imports_commands(p_import):
    conf.from_file('pelconf.yaml')

    p_import.has_calls([
        call('peltak.cli.git'),
        call('peltak.cli.lint'),
        call('peltak.cli.test'),
        call('peltak.cli.version'),
    ])
    assert conf.values == test_config
