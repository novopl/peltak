# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.common import conf


@pytest.mark.parametrize('str_val', [
    'yes',
    'y',
    'true',
    'on'
])
def test_returns_true_for_truthy_string(str_val):
    result = conf.is_true(str_val)

    assert result is True


@pytest.mark.parametrize('str_val', [
    'no',
    'n',
    'false',
    'off',
    'john',
    'hello',
])
def test_returns_false_for_other_values(str_val):
    result = conf.is_true(str_val)

    assert result is False


@pytest.mark.parametrize('str_val', [
    5,
    None,
    5.5,
    {},
    [],
    tuple(),
    set()
])
def test_raises_ValueError_on_non_string_values(str_val):
    with pytest.raises(ValueError):
        conf.is_true(str_val)
