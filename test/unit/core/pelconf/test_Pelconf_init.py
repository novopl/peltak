# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch, MagicMock, Mock, mock_open

# local imports
from peltak.core import conf


@patch('os.path.exists', Mock(return_value=True))
@patch('peltak.core.conf.from_file')
@patch('peltak.core.conf.within_proj_dir', MagicMock())
def test_loads_yaml_config_if_exists(p_from_file):
    conf.init()

    p_from_file.assert_called_once()


@patch('os.path.exists', Mock(return_value=False))
@patch('peltak.core.conf.from_file')
@patch('peltak.core.conf.within_proj_dir', MagicMock())
def test_does_not_load_yaml_config_if_not_found(p_from_file):
    conf.init()

    p_from_file.assert_not_called()


@patch('os.path.exists', Mock(return_value=True))
@patch('builtins.open', mock_open(read_data=''))
@patch('peltak.core.conf.within_proj_dir', MagicMock())
def test_has_initialized_values_if_yaml_is_an_empty_file():
    conf.init()

    assert conf.values is not None
