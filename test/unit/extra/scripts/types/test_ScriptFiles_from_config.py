# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest


# local imports
from peltak.extra.scripts.types import ScriptFiles


def test_works():
    files = ScriptFiles.from_config(dict(
        paths=['src'],
        exclude=['__pycache__'],
        include=['*.py'],
        commit_only=True,
        untracked=False,
    ))

    assert files.paths == ['src']
    assert files.exclude == ['__pycache__']
    assert files.include == ['*.py']
    assert files.commit_only is True
    assert files.untracked is False


def test_works_with_only_paths_defined():
    files = ScriptFiles.from_config({'paths': ['src']})

    assert files.paths == ['src']
    assert list(files.exclude) == []
    assert list(files.include) == []
    assert files.commit_only is False
    assert files.untracked is True


def test_raises_ValueError_if_command_is_not_defined():
    with pytest.raises(ValueError):
        ScriptFiles.from_config({})
