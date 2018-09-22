# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# stdlib imports
import subprocess

# 3rd party imports
import pytest
from mock import Mock, patch

# local imports
from peltak.core import shell


def patch_popen(stdout=None, stderr=None, retcode=0, inject=False):
    p_proc = Mock()
    p_proc.configure_mock(**{
        'communicate.return_value': (stdout, stderr),
        'returncode': retcode
    })
    p_popen = Mock(return_value=p_proc)

    if inject:
        def decorator(fn):
            @patch('subprocess.Popen', p_popen)
            def wrapper(*args, **kw):
                return fn(p_popen, *args, **kw)
            return wrapper

        return decorator

    else:
        return patch('subprocess.Popen', p_popen)


@patch_popen(inject=True)
def test_line_buffered_by_default(p_popen):
    shell.run('hello')

    p_popen.assert_called_once_with('hello', bufsize=1, shell=True)


@patch_popen(retcode=1)
def test_sets_result_fail_status_from_retcode():
    result = shell.run('hello', capture=True)

    assert result.succeeded is False
    assert result.failed is True


@patch_popen(retcode=0)
def test_sets_result_success_status_from_retcode():
    result = shell.run('hello', capture=True)

    assert result.succeeded is True
    assert result.failed is False


@patch_popen(retcode=1)
def test_if_not_given_set_exit_on_error_to_opposite_of_capture():
    with pytest.raises(SystemExit):
        shell.run('hello')

    assert shell.run('hello', capture=True).return_code == 1


@patch_popen(retcode=1)
def test_will_exit_if_exit_on_error_is_set_to_True():
    with pytest.raises(SystemExit):
        shell.run('hello', exit_on_error=True)


@patch_popen(retcode=1)
def test_will_not_exit_if_exit_on_error_is_set_to_False():
    assert shell.run('hello', exit_on_error=False).return_code == 1


@patch_popen(inject=True)
def test_inherits_existing_env_when_env_is_given(p_popen):
    with patch('os.environ', {'fake1': 'env'}):
        shell.run('hello', env={'fake2': 'arg'})

    p_popen.assert_called_once_with(
        'hello',
        env={'fake1': 'env', 'fake2': 'arg'},
        shell=True,
        bufsize=1
    )


@patch_popen(stdout=b'', stderr=b'', inject=True)
def test_setting_capture_to_True_will_pipe_stdout_and_stderr(p_popen):
    shell.run('hello', capture=True)

    p_popen.assert_called_once_with(
        'hello',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1
    )


@patch_popen(stdout='', stderr='', inject=True)
def test_will_not_crash_if_communicated_returns_strings(p_popen):
    shell.run('hello', capture=True)

    p_popen.assert_called_once_with(
        'hello',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1
    )
