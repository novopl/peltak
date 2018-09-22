# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import versioning


@pytest.mark.parametrize('version_str', [
    '1',
    '1.0',
    '1.0.0',
    '0.9',
    '1.3.4',
    '0.239.25',
    '0.0.0',
])
def test_returns_True_for_valid_version_strings(version_str):
    assert versioning.is_valid(version_str) is True


@pytest.mark.parametrize('version_str', [
    'invalid',
    '1.invalid',
    '1.0.0b2',
    '1,9',
    '1.0,9',
])
def test_returns_False_for_invalid_version_strings(version_str):
    assert versioning.is_valid(version_str) is False
