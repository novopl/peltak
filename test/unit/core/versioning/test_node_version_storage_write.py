# pylint: disable=missing-docstring
from unittest.mock import Mock, mock_open, patch

from peltak import testing
from peltak.core import versioning


def patch_open(**kw):
    return patch('peltak.core.versioning.version_file.open', mock_open(**kw))


@testing.patch_pelconf()
@patch('peltak.core.versioning.version_file.exists', Mock(return_value=True))
@patch('peltak.core.fs.write_file')
@patch('json.loads', Mock(return_value={}))
@patch_open()
def test_correctly_replaces_version(p_write_file: Mock):
    storage = versioning.NodeVersionFile('package.json')
    storage.write('1.0.1')

    p_write_file.assert_called_with(
        'package.json',
        '{\n  "version": "1.0.1"\n}\n'
    )
