# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch

# local imports
from peltak import testing
from peltak.core import git


@patch('peltak.core.shell.run')
def test_works_as_expected(p_run):
    git.current_branch()

    p_run.assert_called_once_with('git symbolic-ref --short HEAD', capture=True)


@patch('peltak.core.conf.within_proj_dir')
@patch('peltak.core.shell.run')
def test_runs_the_git_command_in_project_root(p_run, p_within_proj_dir):
    p_run.return_value = testing.mock_result(stdout='name||email')

    assert git.commit_author() == git.Author('name', 'email')

    p_within_proj_dir.assert_called_once_with()
    p_run.assert_called_once_with('git show -s --format="%an||%ae" ',
                                  capture=True)


@patch('peltak.core.conf.within_proj_dir')
@patch('peltak.core.shell.run')
def test_runs_the_git_command_in_project_root(p_run, p_within_proj_dir):
    p_run.return_value = testing.mock_result(stdout='name||email')

    assert git.commit_author() == git.Author('name', 'email')

    p_within_proj_dir.assert_called_once_with()
    p_run.assert_called_once_with('git show -s --format="%an||%ae" ',
                                  capture=True)