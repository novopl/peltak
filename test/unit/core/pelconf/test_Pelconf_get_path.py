# pylint: disable=missing-docstring
from peltak import testing
from peltak.core import conf


@testing.patch_pelconf({})
def test_returns_None_if_given_as_default():
    assert conf.get_path('test', None) is None


@testing.patch_pelconf({})
def test_converts_default_to_abspath():
    assert conf.get_path('test', 'hello') == conf.proj_path('hello')


@testing.patch_pelconf({
    'cfg': {
        'test': 'hello',
    },
})
def test_converts_config_value_to_absolute_path():
    assert conf.get_path('test') == conf.proj_path('hello')
