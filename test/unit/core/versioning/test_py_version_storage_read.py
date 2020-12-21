# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

import pytest

from peltak import testing
from peltak.core import versioning


@pytest.mark.parametrize('version_def,expected', [
    ("__version__ = '0.7.4'", '0.7.4'),
    ("__version__='0.7.4'", '0.7.4'),
    ('__version__ = "0.7.4"', '0.7.4'),
    ('__version__ = "0.7"', '0.7'),
    ('__version__ = "1.0"', '1.0'),
    ('__version__ = "1"', '1'),
])
@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.exists', Mock(return_value=True))
def test_finds_correctly_defined_version(version_def, expected):
    file_data = '\n'.join([
        "# -*- coding: utf-8 -*-",
        version_def,
        "",
    ])
    with patch('peltak.core.versioning.open', mock_open(read_data=file_data)):
        storage = versioning.PyVersionStorage('fake.py')
        version = storage.read()

        assert version == expected


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.exists', Mock(return_value=True))
@patch(
    'peltak.core.versioning.open',
    mock_open(read_data="# -*- coding: utf-8 -*-\n")
)
def test_returns_None_if_cant_find_the_version():
    storage = versioning.PyVersionStorage('fake.py')

    assert storage.read() is None
