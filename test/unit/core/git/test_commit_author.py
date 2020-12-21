# pylint: disable=missing-docstring
from unittest.mock import patch

from peltak import testing
from peltak.core import git


@patch('peltak.core.shell.run')
def test_works_as_expected(p_run):
    git.current_branch().name()

    p_run.assert_called_once_with('git symbolic-ref --short HEAD',
                                  capture=True,
                                  never_pretend=True)


@patch('peltak.core.conf.within_proj_dir')
@patch('peltak.core.shell.run')
def test_runs_the_git_command_in_project_root(p_run, p_within_proj_dir):
    p_run.return_value = testing.mock_result(
        stdout='hash||name||email||title||desc||parent'
    )

    assert git.latest_commit().author == git.Author('name', 'email')

    p_within_proj_dir.assert_called_once_with()
    p_run.assert_called_once_with('git show -s --format="%H||%an||%ae||%s||%b||%P" ',
                                  capture=True,
                                  never_pretend=True)
