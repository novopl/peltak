# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import Mock, patch

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import fs
from peltak.core import types


@patch('peltak.core.fs.filtered_walk')
def test_calls_filtered_walk_with_paths_configured(p_filtered_walk):
    # type: (Mock) -> None
    files = types.FilesCollection.from_config({
        'paths': ['path1', 'path2'],
    })

    fs.collect_files(files)

    assert p_filtered_walk.call_count == 2

    args, _ = p_filtered_walk.call_args_list[0]
    expected = (conf.proj_path('path1'), files.whitelist(), files.blacklist())
    assert tuple(args) == expected

    args, _ = p_filtered_walk.call_args_list[1]
    expected = (conf.proj_path('path2'), files.whitelist(), files.blacklist())
    assert tuple(args) == expected


@patch('peltak.core.fs.filtered_walk', Mock(return_value=[]))
@patch('peltak.core.shell.cprint')
def test_prints_debug_info_if_verbose_lvl_ge_3(p_cprint):
    # type: (Mock) -> None
    files = types.FilesCollection.from_config({
        'paths': ['path1', 'path2'],
    })

    context.RunContext().set('verbose', 3)
    fs.collect_files(files)
    context.RunContext().set('verbose', 0)

    assert next(
        (True for x in p_cprint.call_args_list if 'only_staged: ' in x[0][0]),
        False
    )
    assert next(
        (True for x in p_cprint.call_args_list if 'untracked: ' in x[0][0]),
        False
    )
    assert next(
        (True for x in p_cprint.call_args_list if 'whitelist: ' in x[0][0]),
        False
    )
    assert next(
        (True for x in p_cprint.call_args_list if 'blacklist: ' in x[0][0]),
        False
    )