# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import patch, mock_open, Mock, call

# 3rd party imports
import yaml

# local imports
from peltak.core import conf


test_yaml = '''
version: '0.1'

src_dir: src
src_path: 'src/peltak'
build_dir: .build
version_file: 'src/peltak/__init__.py'

commands:
  - peltak.commands.git
  - peltak.commands.lint
  - peltak.commands.test
  - peltak.commands.version

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
test_config = yaml.load(test_yaml)


@patch('peltak.core.conf.open', mock_open(read_data=test_yaml))
@patch('peltak.core.conf._import', Mock())
def test_properly_loads_all_config_variables():
    conf.load_yaml_config('pelconf.yaml')

    assert conf.g_config == test_config


@patch('peltak.core.conf.open', mock_open(read_data=test_yaml))
@patch('peltak.core.conf._import')
def test_imports_commands(p_import):
    conf.load_yaml_config('pelconf.yaml')

    p_import.has_calls([
        call('peltak.commands.git'),
        call('peltak.commands.lint'),
        call('peltak.commands.test'),
        call('peltak.commands.version'),

    ])
    assert conf.g_config == test_config
