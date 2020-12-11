# pylint: disable=missing-docstring
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from peltak import testing
from peltak.core import conf
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


@patch('peltak.extra.scripts.logic.exec_script_command', Mock(return_value=0))
def test_raises_ValueError_if_command_or_command_files_is_missing():
    # type: () -> None
    """
    GIVEN A script with neither command nor command_file defined
     WHEN I run the script
     THEN it raises ValueError.
    """
    options = {}    # type: Dict[str, Any]
    script = Script(
        name='test',
        command='',
        command_file='',
    )

    with pytest.raises(ValueError):
        run_script(script, options)


@pytest.mark.parametrize('command,command_file', [
    ('', 'fake/file'),
    ('fake-cmd', 'fake/file'),
])
@patch('peltak.extra.scripts.logic.exec_script_command', Mock(return_value=0))
@testing.patch_open('peltak.extra.scripts.logic', read_data='fake command file')
def test_uses_command_file_if_given(p_open, command, command_file):
    # type: (Mock, str, str) -> None
    """
    GIVEN A command_file is defined for the script
     WHEN I run the script
     THEN It will always use it no matter if 'command' is also defined or not
    """
    options = {}    # type: Dict[str, Any]
    script = Script(
        name='test',
        command=command,
        command_file=command_file,
    )

    run_script(script, options)
    p_open.assert_called_once_with(conf.proj_path('fake/file'))


# Used only in type hint comments
del Any, Dict
