# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch

# local imports
from peltak import testing
from peltak.core import git


@patch('peltak.core.shell.run')
def test_calls_git_cli(p_run):
    git.current_branch()

    p_run.assert_called_once_with('git symbolic-ref --short HEAD', capture=True)


@testing.patch_run(stdout='test ')
def test_strips_output_from_git_porcelain():
    assert git.current_branch() == 'test'