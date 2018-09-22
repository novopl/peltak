# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import Mock, mock_open, patch

# 3rd party imports
import pytest

# local imports
from peltak.core import versioning


@pytest.mark.parametrize('version_def,expected', [
    ('{"version": "0.7.4"}', '0.7.4'),
    ('{"version" : "0.7.4"}', '0.7.4'),
    ('{"version":"0.7.4"}', '0.7.4'),
])
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_finds_correctly_defined_version(version_def, expected):
    with patch('peltak.core.versioning.open', mock_open(read_data=version_def)):
        storage = versioning.NodeVersionStorage('package.js')
        version = storage.read()

        assert version == expected


@patch('peltak.core.versioning.exists', Mock(return_value=True))
@patch(
    'peltak.core.versioning.open',
    mock_open(read_data='{"name": "proj"}')
)
def test_returns_None_if_cant_find_the_version():
    storage = versioning.NodeVersionStorage('package.js')

    assert storage.read() is None
