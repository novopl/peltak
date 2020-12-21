# pylint: disable=missing-docstring
from unittest.mock import patch

from peltak import testing
from peltak.core import git
from peltak.core import util


@patch('peltak.core.shell.run')
def test_calls_git_cli(p_run):
    util.cached_result.clear(git.current_branch)

    git.current_branch().name

    p_run.assert_called_once_with('git symbolic-ref --short HEAD',
                                  capture=True,
                                  never_pretend=True)


@testing.patch_run(stdout='test ')
def test_strips_output_from_git_porcelain():
    util.cached_result.clear(git.current_branch)

    assert git.current_branch().name == 'test'
