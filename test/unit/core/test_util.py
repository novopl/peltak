# pylint: disable=missing-docstring
from unittest.mock import patch, Mock

import pytest

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
    # TODO: Use freezegun here
    @patch('time.time', Mock(side_effect=[1, 2]))
    def test_returns_proper_results(self):

        with util.timed_block() as t:
            pass

        assert t.elapsed == 1
        assert t.elapsed_ms == 1000
        assert t.elapsed_s == 1


class TestGetFromDict:
    @pytest.fixture
    def test_dict(self):
        yield {
            'root': 'root value',
            'test1': {
                'sub': 'nested value'
            }
        }

    @pytest.mark.parametrize('query,expected', [
        ('root', 'root value'),
        ('test1.sub', 'nested value'),
        ('test1', {'sub': 'nested value'}),
    ])
    def test_returns_correct_values(self, test_dict, query, expected):
        assert util.get_from_dict(test_dict, query) == expected

    @pytest.mark.parametrize('query', [
        'test1.invalid',
        'invalid.sub'
    ])
    def test_return_default_when_provided_and_value_not_found(self, test_dict, query):
        assert util.get_from_dict(test_dict, query, -1) == -1

    @pytest.mark.parametrize('query', [
        'test1.invalid',
        'invalid',
        'invalid.sub',
    ])
    def test_raises_KeyError_if_default_not_given(self, query, test_dict):
        with pytest.raises(KeyError):
            util.get_from_dict(test_dict, query)


class TestSetInDict:
    def test_can_set_root_value(ctx):
        d = {}
        util.set_in_dict(d, 'test', 'value')

        assert d == {'test': 'value'}

    def test_can_set_sub_value(ctx):
        d = {}
        util.set_in_dict(d, 'test.sub', 'value')

        assert d == {'test': {'sub': 'value'}}

    def test_raises_KeyError_if_part_of_the_path_is_not_a_dict(ctx):
        d = {'test': 'value'}

        with pytest.raises(KeyError):
            util.set_in_dict(d, 'test.sub', 'value')

        with pytest.raises(KeyError):
            util.set_in_dict(d, 'test.sub.sub', 'value')
