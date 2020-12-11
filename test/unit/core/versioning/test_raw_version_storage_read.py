# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

import pytest

from peltak.core import versioning


@pytest.mark.parametrize('version_def,expected', [
    ('0.7.4', '0.7.4'),
    ('\n0.7.4', '0.7.4'),
    ('0.7.4\n', '0.7.4'),
    ('\n\t 0.7.4\n\t', '0.7.4'),
])
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_finds_correctly_defined_version(version_def, expected):
    with patch('peltak.core.versioning.open', mock_open(read_data=version_def)):
        storage = versioning.RawVersionStorage('package.js')
        version = storage.read()

        assert version == expected


@patch('peltak.core.versioning.exists', Mock(return_value=True))
@patch('peltak.core.versioning.open', mock_open(read_data='invalid'))
def test_returns_None_if_cant_find_the_version():
    storage = versioning.RawVersionStorage('package.js')

    assert storage.read() is None
