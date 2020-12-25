# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak.core import versioning


@patch('peltak.core.versioning.load_version_file')
def test_uses_version_storage_to_get_project_version(p_load_version_file, app_conf):
    mock_ver_file = Mock()
    p_load_version_file.return_value = mock_ver_file

    versioning.current()

    p_load_version_file.assert_called_once_with('VERSION')
    mock_ver_file.read.assert_called_once_with()
