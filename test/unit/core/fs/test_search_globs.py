# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import fs


@pytest.mark.parametrize('path,patterns,expected', [
    ('/fake/path', ['invalid', '/path'], False),
    ('/fake/path', ['/fake*'], True),
    ('/fake/path', ['fake'], True),
    ('/fake/path', ['fake*'], True),
    ('/fake/path', ['path'], True),
])
def test_properly_searches_path_for_globs(path, patterns, expected):
    assert fs.search_globs(path, patterns) == expected
