# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

import pytest

from peltak.core import versioning


@patch('peltak.core.versioning.load_version_file')
def test_uses_VersionStorage(p_load_version_file, app_conf):
    mock_ver_file = Mock()
    p_load_version_file.return_value = mock_ver_file

    versioning.write('0.1.1')

    p_load_version_file.assert_called_once()
    mock_ver_file.write.assert_called_once_with('0.1.1')


def test_raises_ValueError_if_invalid_version_is_given(app_conf):
    with pytest.raises(ValueError):
        versioning.write('invalid')
