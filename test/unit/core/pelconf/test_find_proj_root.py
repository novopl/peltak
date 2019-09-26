# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# local imports
from peltak import testing
from peltak.core import pelconf
from peltak.core import util


@testing.patch_proj_root('/fake/proj/root')
def test_runs_detection_when_no_global_variable_stored():
    util.cached_result.clear(pelconf._find_proj_root)
    assert pelconf._find_proj_root() == '/fake/proj/root'

    util.cached_result.clear(pelconf._find_proj_root)


@testing.patch_proj_root('/fake/proj/root', nest_level=2)
def test_works_with_multiple_levels_of_nesting():
    util.cached_result.clear(pelconf._find_proj_root)
    assert pelconf._find_proj_root() == '/fake/proj/root'

    util.cached_result.clear(pelconf._find_proj_root)


@testing.patch_proj_root(None)
def test_returns_none_if_not_found():
    util.cached_result.clear(pelconf._find_proj_root)
    assert pelconf._find_proj_root() is None

    util.cached_result.clear(pelconf._find_proj_root)
