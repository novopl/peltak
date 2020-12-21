# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

import pytest

from peltak import testing
from peltak.core import versioning


def patch_open(**kw):
    return patch('peltak.core.versioning.open', mock_open(**kw))


@pytest.mark.parametrize('version_def,expected', [
    ("__version__ = '0.7.4'", "__version__ = '1.0.1'"),
    ("__version__='0.7.4'", "__version__ = '1.0.1'"),
    ('__version__ = "0.7.4"', "__version__ = '1.0.1'"),
    ('__version__ = "0.7"', "__version__ = '1.0.1'"),
    ('__version__ = "1.0"', "__version__ = '1.0.1'"),
    ('__version__ = "1"', "__version__ = '1.0.1'"),
])
@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.exists', Mock(return_value=True))
@patch('peltak.core.fs.write_file')
def test_correctly_replaces_version(p_write_file, version_def, expected):
    # type: (Mock, str, str) -> None
    file_data = '\n'.join([
        "# -*- coding: utf-8 -*-",
        version_def,
        "",
    ])
    expected_data = '\n'.join([
        "# -*- coding: utf-8 -*-",
        expected,
        "",
    ])

    with patch_open(read_data=file_data):
        storage = versioning.PyVersionStorage('fake.py')
        storage.write('1.0.1')

        p_write_file.assert_called_once_with(
            'fake.py',
            expected_data
        )
