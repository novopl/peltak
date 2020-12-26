# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

import pytest

from peltak.core import versioning


def patch_open(**kw):
    return patch('peltak.core.versioning.version_file.open', mock_open(**kw))


@pytest.mark.parametrize('version_def,expected', [
    ('0.7.4', '0.7.4'),
    ('\n0.7.4', '0.7.4'),
    ('0.7.4\n', '0.7.4'),
    ('\n\t 0.7.4\n\t', '0.7.4'),
])
@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
def test_finds_correctly_defined_version(version_def, expected):
    with patch_open(read_data=version_def):
        version_file = versioning.RawVersionFile('package.js')
        version = version_file.read()

        assert version == expected


@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
@patch_open(read_data='invalid')
def test_returns_None_if_cant_find_the_version():
    version_file = versioning.RawVersionFile('package.js')

    assert version_file.read() is None
