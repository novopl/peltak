# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import pytest

from peltak.core import context


def test_get_existing_root_value_works(ctx):
    ctx.values = {
        'test1': 'test value',
    }

    assert context.get('test1') == 'test value'


def test_get_existing_nested_value_works(ctx):
    ctx.values = {
        'test1': {
            'sub': 'test value',
        }
    }

    assert context.get('test1.sub') == 'test value'


def test_can_just_get_the_full_nested_object(ctx):
    ctx.values = {
        'test1': {
            'sub': 'test value',
        }
    }

    assert context.get('test1') == {'sub': 'test value'}


@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
def test_return_default_when_provided_and_value_not_found(ctx, query):
    ctx.values = {
        'test1': {
            'sub': 'test value',
        }
    }
    assert context.get(query, -1) == -1


@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
def test_raises_AttributeError_if_default_not_given(ctx, query):
    ctx.values = {
        'test1': {
            'sub': 'test value',
        }
    }

    with pytest.raises(AttributeError):
        context.get(query)
