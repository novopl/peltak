# pylint: disable=missing-docstring
from unittest.mock import patch, Mock

from peltak.core import util


class TestCachedResults:
    def test_caching_works(self):
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

    def test_clear_deletes_the_cached_attr(self):
        @util.cached_result()
        def foo():
            pass

        foo()
        assert hasattr(foo, util.cached_result.CACHE_VAR)

        util.cached_result.clear(foo)
        assert not hasattr(foo, util.cached_result.CACHE_VAR)

    def test_can_call_clear_on_uncalled_function(self):
        @util.cached_result()
        def foo():
            pass

        util.cached_result.clear(foo)


class TestTimedBlock:
    @patch('time.time', Mock(side_effect=[1, 2]))
    def test_returns_proper_results(self):

        with util.timed_block() as t:
            pass

        assert t.elapsed == 1
        assert t.elapsed_ms == 1000
        assert t.elapsed_s == 1
