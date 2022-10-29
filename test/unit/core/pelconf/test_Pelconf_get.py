# pylint: disable=missing-docstring
import pytest

from peltak.core import conf


def test_cannot_get_values_from_config_root():
    app_conf = conf.Config({'test1': 'test value'})
    with pytest.raises(AttributeError):
        app_conf.get('test1')


def test_will_actually_get_values_from_the_cfg_section():
    app_conf = conf.Config({
        'test1': 'unavailable value',
        'cfg': {
            'test1': 'config value'
        }})
    assert app_conf.get('test1') == 'config value'


def test_get_existing_nested_value_works():
    app_conf = conf.Config({
        'cfg': {
            'test1': {
                'sub': 'test value',
            },
        },
    })
    assert app_conf.get('test1.sub') == 'test value'


def test_can_just_get_the_full_nested_object():
    app_conf = conf.Config({
        'cfg': {
            'test1': {
                'sub': 'test value',
            },
        },
    })

    assert app_conf.get('test1') == {'sub': 'test value'}


@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
def test_return_default_when_provided_and_value_not_found(query):
    """ Return default when provided and value not found.

    And the second line
    """
    app_conf = conf.Config({
        'test1': {
            'sub': 'test value',
        }
    })

    assert app_conf.get(query, -1) == -1
    assert app_conf.get(query, -1) == -1


@pytest.mark.parametrize('query', [
    'test1.invalid',
    'invalid.sub'
])
def test_raises_AttributeError_if_default_not_given(query):
    app_conf = conf.Config({
        'test1': {
            'sub': 'test value',
        }
    })

    with pytest.raises(AttributeError):
        app_conf.get(query)
