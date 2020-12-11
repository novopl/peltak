# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak import testing
from peltak.core import versioning


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.get_version_storage')
def test_uses_VersionStorage(p_get_version_storage):
    mock_storage = Mock()
    p_get_version_storage.return_value = mock_storage

    versioning.write('0.1.1')

    p_get_version_storage.assert_called_once_with()
    mock_storage.write.assert_called_once_with('0.1.1')


@testing.patch_pelconf({'version_file': 'fake.yaml'})
@patch('peltak.core.versioning.get_version_storage', Mock())
def test_raises_ValueError_if_invalid_version_is_given():
    with pytest.raises(ValueError):
        versioning.write('invalid')
