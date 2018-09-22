# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import fs


@pytest.mark.parametrize('path,patterns,expected', [
    ('/fake/path', ['fake', '/fake', 'path'], False),
    ('/fake/path', ['*fake*'], True),
    ('/fake/path', ['/fake*'], True),
    ('/fake/path', ['*ke/pa*'], True),
])
def test_properly_matches_globs(path, patterns, expected):
    assert fs.match_globs(path, patterns) == expected
