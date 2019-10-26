# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest


# local imports
from peltak.core.types import FilesCollection


def test_works():
    files = FilesCollection.from_config(dict(
        paths=['src'],
        exclude=['__pycache__'],
        include=['*.py'],
        only_staged=True,
        untracked=False,
    ))

    assert files.paths == ['src']
    assert files.exclude == ['__pycache__']
    assert files.include == ['*.py']
    assert files.only_staged is True
    assert files.untracked is False


def test_works_with_only_paths_defined():
    files = FilesCollection.from_config({'paths': ['src']})

    assert files.paths == ['src']
    assert list(files.exclude) == []
    assert list(files.include) == []
    assert files.only_staged is False
    assert files.untracked is True


def test_raises_ValueError_if_command_is_not_defined():
    with pytest.raises(ValueError):
        FilesCollection.from_config({})


def test_can_specify_a_single_path_as_just_a_string():
    files = FilesCollection.from_config(dict(paths='src'))

    assert files.paths == ['src']


def test_can_specify_single_include_path_as_just_a_string():
    files = FilesCollection.from_config(dict(
        paths='src',
        include='*.py'
    ))
    assert files.include == ['*.py']


def test_can_specify_single_exclude_path_as_just_a_string():
    files = FilesCollection.from_config(dict(
        paths='src',
        exclude='*.pyc'
    ))
    assert files.exclude == ['*.pyc']
