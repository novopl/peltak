# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import Mock, mock_open, patch

# 3rd party imports
import pytest

# local imports
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
def test_correctly_replaces_version(version_def, expected):
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

    with patch_open(read_data=file_data) as p_open:
        storage = versioning.PyVersionStorage('fake.py')
        storage.write('1.0.1')

        fp = p_open()
        fp.write.assert_called_once_with(expected_data)
