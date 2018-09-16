# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import patch

# 3rd party imports
import pytest

# local imports
from peltak.core import conf


def patch_pelconf(config):
    def decorator(fn):
        return patch('peltak.core.conf.g_config', config)(fn)

    return decorator


@patch_pelconf({
    'test1': 'test value',
})
def test_get_existing_root_value_works():
    assert conf.get('test1') == 'test value'


@patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
def test_get_existing_nested_value_works():
    assert conf.get('test1.sub') == 'test value'


@patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
def test_can_just_get_the_full_nested_object():
    assert conf.get('test1') == {'sub': 'test value'}


@patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
def test_return_default_when_provided_and_value_not_found(query):
    assert conf.get(query, -1) == -1
    assert conf.get(query, -1) == -1


@patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
def test_raises_AttributeError_if_default_not_given_and_value_not_found(query):
    with pytest.raises(AttributeError):
        conf.get(query)
