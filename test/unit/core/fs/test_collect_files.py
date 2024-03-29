# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak import testing
from peltak.core import conf, context, fs, types


@patch('peltak.core.fs.filtered_walk')
@testing.patch_pelconf()
def test_calls_filtered_walk_with_paths_configured(p_filtered_walk: Mock):
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
@testing.patch_pelconf()
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


@patch('peltak.core.git.staged', Mock(return_value=['file1.txt', 'file2.yml']))
@testing.patch_pelconf()
def test_return_empty_list_if_none_of_the_whitelisted_files_are_staged():
    """
    GIVEN files collection has a non-empty whitelist and only_staged == True
     WHEN no staged files match the whitelist
     THEN return empty list.
    """
    files = types.FilesCollection.from_config({
        'paths': ['path1'],
        'include': ['*.py'],
        'only_staged': True,
    })

    assert fs.collect_files(files) == []
