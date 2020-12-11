# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from unittest.mock import patch

from peltak.core.types import FilesCollection


def test_contains_elements_from_include_property():
    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'include': ['*.py', '*.yaml', '*.js'],
    })

    assert files.whitelist() == ['*.py', '*.yaml', '*.js']


@patch('peltak.core.git.staged')
def test_uses_staged_files_if_only_staged_is_True(p_git_staged):
    p_git_staged.return_value = ['some', 'fake', 'files']

    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'only_staged': True,
    })

    assert files.whitelist() == ['*some', '*fake', '*files']


@patch('peltak.core.git.staged')
def test_filters_staged_files_with_include_if_both_are_present(p_git_staged):
    p_git_staged.return_value = ['some.py', 'fake.js', 'files.py']

    files = FilesCollection.from_config({
        'paths': 'src/fake',
        'only_staged': True,
        'include': ['*.py'],
    })

    assert files.whitelist() == ['*some.py', '*files.py']


def test_returns_empty_list_if_no_includes_and_commit_is_False():
    files = FilesCollection.from_config({'paths': 'src/fake'})

    assert files.whitelist() == []
