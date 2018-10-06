# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# local imports
from peltak import testing
from peltak.core import conf
from peltak.core import util


@testing.patch_proj_root('/fake/proj/root')
def test_runs_detection_when_no_global_variable_stored():
    assert conf._find_proj_root() == '/fake/proj/root'


@testing.patch_proj_root('/fake/proj/root', nest_level=2)
def test_works_with_multiple_levels_of_nesting():
    assert conf._find_proj_root() == '/fake/proj/root'


@testing.patch_proj_root(None)
def test_returns_none_if_not_found():
    util.cached_result.clear(conf._find_proj_root)
    assert conf._find_proj_root() is None
