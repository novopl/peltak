# pylint: disable=missing-docstring
from unittest.mock import Mock, patch

from peltak.core.scripts.logic import exec_script_command


@patch('subprocess.Popen')
def test_executes_the_command_if_pretend_is_False(p_Popen, app_conf):
    exec_script_command('fake-cmd', False)

    p_Popen.assert_called_once_with('fake-cmd', shell=True)


@patch('subprocess.Popen')
def test_does_not_execute_the_command_if_pretend_is_True(p_Popen):
    exec_script_command('fake-cmd', True)

    p_Popen.assert_not_called()


@patch('subprocess.Popen')
def test_passes_the_script_return_code_to_the_caller(p_Popen, app_conf):
    p_proc = Mock()
    p_Popen.return_value = p_proc
    p_proc.returncode = -99

    result = exec_script_command('fake-cmd', False)

    assert result == -99


@patch('subprocess.Popen')
def test_prints_return_code_to_stdout(p_Popen, app_conf):
    p_proc = Mock()
    p_Popen.return_value = p_proc
    p_proc.returncode = -99

    result = exec_script_command('fake-cmd', False)

    assert result == -99


@patch('subprocess.Popen')
def test_will_kill_subprocess_if_KeyboardInterrupt_is_raised(p_Popen, app_conf):
    p_proc = Mock()
    p_Popen.return_value = p_proc
    p_proc.communicate.side_effect = KeyboardInterrupt()

    result = exec_script_command('fake-cmd', False)

    assert result == -1
    p_proc.kill.assert_called_once()
