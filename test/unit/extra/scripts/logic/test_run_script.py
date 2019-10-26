# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Dict

# 3rd party imports
from mock import Mock, patch

# local imports
from peltak import testing
from peltak.core.context import RunContext
from peltak.extra.scripts.types import Script
from peltak.extra.scripts.logic import run_script


@patch('peltak.extra.scripts.logic.exec_script_command')
def test_works(p_exec_script_command):
    # type: (Mock) -> None
    p_exec_script_command.return_value = 0
    options = {}    # type: Dict[str, Any]
    script = Script.from_config('test', {
        'command': 'fake-cmd'
    })

    run_script(script, options)

    p_exec_script_command.assert_called_once()


@patch('sys.exit')
@patch('peltak.extra.scripts.logic.exec_script_command')
def test_exits_with_script_return_code_if_its_non_zero(p_exec_script_command,
                                                       p_exit):
    # type: (Mock, Mock) -> None
    p_exec_script_command.return_value = -99
    options = {}    # type: Dict[str, Any]
    script = Script.from_config('test', {
        'command': 'fake-cmd'
    })

    run_script(script, options)

    p_exit.assert_called_once_with(-99)


@testing.patch_is_tty(False)
@patch('sys.exit', Mock())
@patch('peltak.core.shell.cprint')
@patch('peltak.extra.scripts.logic.exec_script_command')
def test_prints_return_code_if_verbose_lvl_ge_3(p_exec_script_command,
                                                p_cprint):
    # type: (Mock, Mock) -> None
    RunContext().set('verbose', 1)
    p_exec_script_command.return_value = -99
    options = {}    # type: Dict[str, Any]
    script = Script.from_config('test', {
        'command': 'fake-cmd'
    })

    run_script(script, options)

    assert next(
        (True for x in p_cprint.call_args_list
         if 'Script exited with code: <33>-99' in x[0][0]),
        False
    )


@testing.patch_is_tty(False)
@patch('sys.exit', Mock())
@patch('peltak.core.shell.cprint')
@patch('peltak.extra.scripts.logic.exec_script_command')
def test_prints_template_context_if_verbose_lvl_ge_3(p_exec_script_command,
                                                     p_cprint):
    # type: (Mock, Mock) -> None
    RunContext().set('verbose', 3)
    p_exec_script_command.return_value = -99
    options = {}    # type: Dict[str, Any]
    script = Script.from_config('test', {
        'command': 'fake-cmd'
    })

    run_script(script, options)

    assert next(
        (True for x in p_cprint.call_args_list if 'with context' in x[0][0]),
        False
    )


def assert_(calls, predicate):
    for c in calls:
        predicate(c)
    pass


# Used only in type hint comments
del Any, Dict
