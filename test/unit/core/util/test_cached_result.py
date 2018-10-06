# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

from peltak.core import util


def test_caching_works():
    @util.cached_result()
    def foo():
        call_count = getattr(foo, 'call_count', 0)
        call_count += 1
        setattr(foo, 'call_count', call_count)

    foo()
    assert foo.call_count == 1

    foo()
    assert foo.call_count == 1

    util.cached_result.clear(foo)

    foo()
    assert foo.call_count == 2


def test_clear_deletes_the_cached_attr():
    @util.cached_result()
    def foo():
        pass

    foo()
    assert hasattr(foo, util.cached_result.CACHE_VAR)

    util.cached_result.clear(foo)
    assert not hasattr(foo, util.cached_result.CACHE_VAR)


def test_can_call_clear_on_uncalled_function():
    @util.cached_result()
    def foo():
        pass

    util.cached_result.clear(foo)
