# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import patch

# local imports
from peltak.core.types import FilesCollection


@patch('peltak.core.git.ignore')
def test_by_default_contains_entries_from_gitignore(p_git_ignore):
    p_git_ignore.return_value = ['some', 'fake', 'files']

    files = FilesCollection.from_config({
        'paths': 'src/fake',
    })

    assert files.blacklist() == ['some', 'fake', 'files']


def test_contains_only_elements_from_exclude_if_use_gitignore_is_False():
    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'exclude': ['*.py', '*.yaml', '*.js'],
        'use_gitignore': False,
    })

    assert files.blacklist() == ['*.py', '*.yaml', '*.js']


@patch('peltak.core.git.untracked')
def test_contains_untracked_files_if_untracked_is_set_to_False(p_git_untracked):
    p_git_untracked.return_value = ['some', 'fake', 'files']

    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'use_gitignore': False,
        'untracked': False,
    })

    assert frozenset(files.blacklist()) == frozenset([
        'some',
        'fake',
        'files',
    ])


@patch('peltak.core.git.untracked')
@patch('peltak.core.git.ignore')
def test_combines_everything_into_one_list(p_git_ignore, p_git_untracked):
    p_git_untracked.return_value = ['untracked1', 'untracked2']
    p_git_ignore.return_value = ['ignored1', 'ignored2']

    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'exclude': ['excluded1', 'excluded2'],
        'untracked': False,
    })

    assert frozenset(files.blacklist()) == frozenset([
        'untracked1',
        'untracked2',
        'ignored1',
        'ignored2',
        'excluded1',
        'excluded2',
    ])


def test_returns_empty_list_if_no_exclude_and_use_gitignore_is_False():
    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'use_gitignore': False,
    })

    assert files.whitelist() == []
