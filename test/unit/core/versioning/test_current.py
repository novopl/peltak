# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak import testing
from peltak.core import versioning


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.get_version_storage')
def test_uses_version_storage_to_get_project_version(p_get_version_storage):
    mock_storage = Mock()
    p_get_version_storage.return_value = mock_storage

    versioning.current()

    p_get_version_storage.assert_called_once_with()
    mock_storage.read.assert_called_once_with()
