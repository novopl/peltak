# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch, Mock

# local imports
from peltak.core import conf


@patch('os.path.exists', Mock(side_effect=[True, True]))
@patch('peltak.core.conf.load_yaml_config')
@patch('peltak.core.conf.load_py_config')
def test_allows_having_both_yaml_and_py_configs_together(p_load_py_config,
                                                         p_load_yaml_config):
    conf.load()

    p_load_yaml_config.assert_called_once()
    p_load_py_config.assert_called_once()


@patch('peltak.core.conf.exists', Mock(side_effect=[False, True]))
@patch('peltak.core.conf.load_yaml_config')
@patch('peltak.core.conf.load_py_config')
def test_does_not_load_yaml_config_if_not_found(p_load_py_config,
                                                p_load_yaml_config):
    conf.load()

    p_load_yaml_config.assert_not_called()
    p_load_py_config.assert_called_once()


@patch('peltak.core.conf.exists', Mock(side_effect=[True, False]))
@patch('peltak.core.conf.load_yaml_config')
@patch('peltak.core.conf.load_py_config')
def test_does_not_load_py_config_if_not_found(p_load_py_config,
                                              p_load_yaml_config):
    conf.load()

    p_load_yaml_config.assert_called_once()
    p_load_py_config.assert_not_called()