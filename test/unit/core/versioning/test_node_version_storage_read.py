# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

import pytest

from peltak.core import versioning


def patch_open(**kw):
    return patch('peltak.core.versioning.version_file.open', mock_open(**kw))


@pytest.mark.parametrize('version_def,expected', [
    ('{"version": "0.7.4"}', '0.7.4'),
    ('{"version" : "0.7.4"}', '0.7.4'),
    ('{"version":"0.7.4"}', '0.7.4'),
])
@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
def test_finds_correctly_defined_version(version_def, expected):
    with patch_open(read_data=version_def):
        storage = versioning.NodeVersionFile('package.js')
        version = storage.read()

        assert version == expected


@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
@patch_open(read_data='{"name": "proj"}')
def test_returns_None_if_cant_find_the_version():
    storage = versioning.NodeVersionFile('package.js')

    assert storage.read() is None
