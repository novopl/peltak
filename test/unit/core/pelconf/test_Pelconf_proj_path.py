# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak import testing
from peltak.core import conf
from peltak.core import pelconf
from peltak.core import util


@pytest.mark.parametrize('proj_path,abs_path', [
    ('testfile', '/fake/proj/testfile'),
    ('sub/testfile', '/fake/proj/sub/testfile'),
    ('/abs/path', '/abs/path'),
])
def test_converts_project_path_to_an_absolute_path(proj_path, abs_path):
    # Patch project root location
    setattr(pelconf._find_proj_root, util.cached_result.CACHE_VAR, '/fake/proj')
    assert conf.proj_path(proj_path) == abs_path

    util.cached_result.clear(pelconf._find_proj_root)


@testing.patch_proj_root(None)
def test_returns_input_path_if_no_project_root_found():
    setattr(pelconf._find_proj_root, util.cached_result.CACHE_VAR, None)
    assert conf.proj_path('hello/world') == 'hello/world'

    util.cached_result.clear(pelconf._find_proj_root)


def test_can_join_paths():
    setattr(pelconf._find_proj_root, util.cached_result.CACHE_VAR, '/fake/proj')

    assert conf.proj_path('sub', 'testfile') == '/fake/proj/sub/testfile'

    util.cached_result.clear(pelconf._find_proj_root)


def test_works_with_abspath_split_into_parts():
    setattr(pelconf._find_proj_root, util.cached_result.CACHE_VAR, '/fake/proj')

    assert conf.proj_path('/sub', 'testfile') == '/sub/testfile'

    util.cached_result.clear(pelconf._find_proj_root)
