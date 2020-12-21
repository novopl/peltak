# pylint: disable=missing-docstring
from unittest.mock import Mock

import pytest

from peltak.core.hooks import HooksRegister


def test_is_called_when_subscribed():
    fake_handler = Mock()
    register = HooksRegister()

    register('fake-hook')(fake_handler)
    register.call('fake-hook')

    fake_handler.assert_called_once_with()


def test_is_not_called_after_unsubscribed():
    conf = {}
    fake_handler = Mock()
    register = HooksRegister()

    register('fake-hook')(fake_handler)
    register.remove('fake-hook', fake_handler)
    register.call('fake-hook', conf)

    fake_handler.assert_not_called()


def test_passes_arguments_to_the_hooks():
    param = {'name': 'hello'}
    fake_handler = Mock()
    register = HooksRegister()

    register('fake-hook')(fake_handler)
    register.call('fake-hook', param, 1)

    fake_handler.assert_called_once_with(param, 1)


def test_can_register_hooks_with_decorator():
    fake_fn = Mock()
    register = HooksRegister()

    @register('fake-hook')
    def post_conf_load():       # pylint: disable=unused-variable
        fake_fn()

    register.call('fake-hook')

    fake_fn.assert_called_once_with()


def test_registering_with_empty_name_raises_ValueError():
    fake_handler = Mock()
    register = HooksRegister()

    with pytest.raises(ValueError):
        register('')(fake_handler)


def test_calling_a_hook_with_empty_name_raises_ValueError():
    register = HooksRegister()

    with pytest.raises(ValueError):
        register.call('')


def test_trying_to_remove_unregistered_hook_raises_ValueError():
    fake_handler1 = Mock()
    fake_handler2 = Mock()
    register = HooksRegister()

    with pytest.raises(ValueError):
        register.remove('fake-hook', fake_handler1)

    register('fake-hook')(fake_handler2)

    with pytest.raises(ValueError):
        register.remove('fake-hook', fake_handler1)


def test_registering_hook_twice_raises_ValueError():
    fake_handler = Mock()
    register = HooksRegister()

    register('fake-hook')(fake_handler)

    with pytest.raises(ValueError):
        register('fake-hook')(fake_handler)
