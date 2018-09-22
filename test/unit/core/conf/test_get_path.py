# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import patch

# local imports
from peltak.core import conf


def patch_pelconf(config):
    def decorator(fn):
        return patch('peltak.core.conf.g_config', config)(fn)

    return decorator


@patch_pelconf({})
def test_returns_None_if_given_as_default():
    assert conf.get_path('test', None) is None


@patch_pelconf({})
def test_converts_default_to_abspath():
    assert conf.get_path('test', 'hello') == conf.proj_path('hello')


@patch_pelconf({
    'test': 'hello'
})
def test_converts_config_value_to_absolute_path():
    assert conf.get_path('test') == conf.proj_path('hello')
