# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
import pytest

from peltak.core import fs


@pytest.mark.parametrize('path,patterns,expected', [
    ('/fake/path', ['fake'], False),
    ('/fake/path', ['path'], False),
    ('/fake/path', ['/fake'], False),
    ('/fake/path', ['*fake*'], True),
    ('/fake/path', ['/fake*'], True),
    ('/fake/path', ['*ke/pa*'], True),
])
def test_properly_matches_globs(path, patterns, expected):
    assert fs.match_globs(path, patterns) == expected


def test_all_patterns_are_tested():
    assert fs.match_globs('/fake/path', ['invalid', '/fake*']) is True
