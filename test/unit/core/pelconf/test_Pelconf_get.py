# pylint: disable=missing-docstring
import pytest

from peltak.core import conf
from peltak import testing


@testing.patch_pelconf({
    'test1': 'test value',
})
def test_get_existing_root_value_works():
    assert conf.get('test1') == 'test value'


@testing.patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
def test_get_existing_nested_value_works():
    assert conf.get('test1.sub') == 'test value'


@testing.patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
def test_can_just_get_the_full_nested_object():
    assert conf.get('test1') == {'sub': 'test value'}


@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
@testing.patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
def test_return_default_when_provided_and_value_not_found(query):
    """ Return default when provided and value not found.

    And the second line
    """
    assert conf.get(query, -1) == -1
    assert conf.get(query, -1) == -1


@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
@testing.patch_pelconf({
    'test1': {
        'sub': 'test value',
    }
})
def test_raises_AttributeError_if_default_not_given(query):
    with pytest.raises(AttributeError):
        conf.get(query)
