# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak.core.templates.filters import wrap_paths_filter


@patch('peltak.core.fs.wrap_paths')
def test_calls_fs_wrap_paths_internally(p_fs_wrap_paths: Mock):
    wrap_paths_filter(['fake', 'paths'])

    p_fs_wrap_paths.assert_called_once_with(['fake', 'paths'])
