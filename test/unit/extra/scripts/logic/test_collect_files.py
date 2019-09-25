# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import Mock, patch

# local imports
from peltak.core import conf
from peltak.extra.scripts.types import ScriptFiles
from peltak.extra.scripts.logic import collect_files


@patch('peltak.core.fs.filtered_walk')
def test_calls_filtered_walk_with_paths_configured(p_filtered_walk):
    # type: (Mock) -> None
    files = ScriptFiles.from_config({
        'paths': ['path1', 'path2'],
    })

    collect_files(files)

    assert p_filtered_walk.call_count == 2

    args, _ = p_filtered_walk.call_args_list[0]
    expected = (conf.proj_path('path1'), files.whitelist(), files.blacklist())
    assert tuple(args) == expected

    args, _ = p_filtered_walk.call_args_list[1]
    expected = (conf.proj_path('path2'), files.whitelist(), files.blacklist())
    assert tuple(args) == expected


# Used only in type hint comments
del Mock
