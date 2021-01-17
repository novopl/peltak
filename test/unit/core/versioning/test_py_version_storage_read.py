# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

import pytest

from peltak import testing
from peltak.core import versioning


def patch_open(**kw):
    return patch('peltak.core.versioning.version_file.open', mock_open(**kw))


@pytest.mark.parametrize('version_def,expected', [
    ("__version__ = '0.7.4'", '0.7.4'),
    ("__version__='0.7.4'", '0.7.4'),
    ('__version__ = "0.7.4"', '0.7.4'),
    ('__version__ = "0.7"', '0.7'),
    ('__version__ = "1.0"', '1.0'),
    ('__version__ = "1"', '1'),
])
@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
def test_finds_correctly_defined_version(app_conf, version_def, expected):
    file_data = '\n'.join([
        "# -*- coding: utf-8 -*-",
        version_def,
        "",
    ])
    with patch_open(read_data=file_data):
        version_file = versioning.PyVersionFile('fake.py')
        version = version_file.read()

        assert version == expected


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
@patch_open(read_data="# -*- coding: utf-8 -*-\n")
def test_returns_None_if_cant_find_the_version():
    version_file = versioning.PyVersionFile('fake.py')

    assert version_file.read() is None
