# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak.core.templates.filters import wrap_paths


@patch('peltak.core.fs.wrap_paths')
def test_calls_fs_wrap_paths_internally(p_fs_wrap_paths):
    # type: (Mock) -> None

    wrap_paths(['fake', 'paths'])

    p_fs_wrap_paths.assert_called_once_with(['fake', 'paths'])


# Used only in type hint comments
del Mock
