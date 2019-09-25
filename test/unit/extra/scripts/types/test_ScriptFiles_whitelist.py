# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import patch

# local imports
from peltak.extra.scripts.types import ScriptFiles


def test_contains_elements_from_include_property():
    files = ScriptFiles.from_config({
        'paths': 'src/fake',
        'include': ['*.py', '*.yaml', '*.js'],
    })

    assert files.whitelist() == ['*.py', '*.yaml', '*.js']


@patch('peltak.core.git.staged')
def test_uses_staged_files_if_commit_prop_is_True_and_no_include_given(p_git_staged):
    p_git_staged.return_value = ['some', 'fake', 'files']

    files = ScriptFiles.from_config({
        'paths': 'src/fake',
        'commit': True,
    })

    assert files.whitelist() == ['*some', '*fake', '*files']


@patch('peltak.core.git.staged')
def test_combines_staged_files_with_defined_includes(p_git_staged):
    p_git_staged.return_value = ['some', 'fake', 'files']

    files = ScriptFiles.from_config({
        'paths': 'src/fake',
        'commit': True,
        'include': ['*.py', '*.yaml', '*.js'],
    })

    assert frozenset(files.whitelist()) == frozenset([
        '*some',
        '*fake',
        '*files',
        '*.py',
        '*.yaml',
        '*.js'
    ])


def test_returns_empty_list_if_no_includes_and_commit_is_False():
    files = ScriptFiles.from_config({'paths': 'src/fake'})

    assert files.whitelist() == []
