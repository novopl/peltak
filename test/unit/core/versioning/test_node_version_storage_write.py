# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import Mock, mock_open, patch

# local imports
from peltak import testing
from peltak.core import versioning


def patch_open(**kw):
    return patch('peltak.core.versioning.open', mock_open(**kw))


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.exists', Mock(return_value=True))
@patch('peltak.core.fs.write_file')
@patch('json.loads', Mock(return_value={}))
def test_correctly_replaces_version(p_write_file):
    # type: (Mock) -> None

    with patch_open():
        storage = versioning.NodeVersionStorage('package.json')
        storage.write('1.0.1')

        p_write_file.assert_called_with(
            'package.json',
            '{\n  "version": "1.0.1"\n}'
        )
