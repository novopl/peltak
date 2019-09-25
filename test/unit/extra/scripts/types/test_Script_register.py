# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from mock import Mock, patch

# 3rd party imports
import pytest

# local imports
from peltak.extra.scripts.types import Script


def test_uses_cli_group_command_decorator():
    p_run_cli = Mock()
    p_command_decorator = Mock()
    p_run_cli.command.return_value = p_command_decorator

    script = Script.from_config('fake', {'command': 'fake'})

    script.register(p_run_cli)

    p_run_cli.command.assert_called_with(script.name)
    p_command_decorator.assert_called_once()


@patch('peltak.extra.scripts.types.verbose_option')
def test_every_script_has_verbose_option(p_verbose_option):
    script = Script.from_config('fake', {'command': 'fake'})
    script.register(Mock())

    p_verbose_option.assert_called_once()


@patch('peltak.extra.scripts.types.pretend_option')
def test_every_script_has_pretend_option(p_pretend_option):
    script = Script.from_config('fake', {'command': 'fake'})
    script.register(Mock())

    p_pretend_option.assert_called_once()


@patch('peltak.extra.scripts.types.click')
def test_creates_all_options_defined_in_the_script_config(p_click):
    script = Script.from_config('fake', {
        'command': 'fake',
        'options': [
            {'name': '--fake1', 'is_flag': True},
            {'name': '--fake2', 'type': 'int'},
        ]
    })

    script.register(Mock())

    assert p_click.option.call_count == 2
    assert len(p_click.option.call_args_list) == 2

    fake1 = next(
        (args for args in p_click.option.call_args_list if args[0][0] == '--fake1'),
        None,
    )
    fake2 = next(
        (args for args in p_click.option.call_args_list if args[0][0] == '--fake2'),
        None,
    )

    assert fake1 is not None
    fake_1args, fake1_kw = fake1
    assert fake1_kw['is_flag'] is True
    assert fake1_kw['count'] is False
    assert fake1_kw['help'] == ''
    assert fake1_kw['default'] is None
    assert fake1_kw['type'] is str

    assert fake2 is not None
    fake2_args, fake2_kw = fake2
    assert fake2_kw['is_flag'] is False
    assert fake2_kw['count'] is False
    assert fake2_kw['help'] == ''
    assert fake2_kw['default'] is None
    assert fake2_kw['type'] == int
