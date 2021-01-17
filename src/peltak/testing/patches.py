""" A place to store all patch functions specific to peltak.

Easier to track them down, when you need one.
"""
from functools import wraps
from typing import Any, Optional
from unittest.mock import Mock, mock_open, patch

from peltak.core import conf, shell
from peltak.core.shell import ExecResult


def patch_is_tty(value):
    """ Wrapped test function will have peltak.core.shell.is_tty set to *value*. """
    def decorator(fn):  # pylint: disable=missing-docstring
        @wraps(fn)
        def wrapper(*args, **kw):   # pylint: disable=missing-docstring
            is_tty = shell.is_tty
            shell.is_tty = value

            try:
                return fn(*args, **kw)
            finally:
                shell.is_tty = is_tty
        return wrapper

    return decorator


def patch_proj_root(path):
    """ Overwrite the project root path in conf.Config singleton. """
    from peltak.core import conf

    def decorator(fn):  # pylint: disable=missing-docstring
        @wraps(fn)
        def wrapper(*args, **kw):  # pylint: disable=missing-docstring
            curr_root = conf.g_conf.root_dir
            conf.root_dir = path

            result = fn(*args, **kw)

            conf.root_dir = curr_root
            return result

        return wrapper
    return decorator


def patch_pelconf(
    values: Optional[conf.ConfigDict] = None,
    *,
    path: str = '/fake/proj/pelconf.yaml',
):
    return patch('peltak.core.conf.g_conf', conf.Config(
        values=values,
        path=path,
    ))


def patch_run(
    stdout: Optional[str] = None,
    retcode: Optional[int] = None,
    stderr: Optional[str] = None,
    cmd: Optional[str] = None
) -> Any:
    """ Patch shell.run and make it return a given result.

    Args:
        stdout (str):
        retcode (int):
        stderr (str):
        cmd (str):

    Returns:
        FunctionType:

    """
    p_run = Mock(return_value=ExecResult(
        cmd or '',
        retcode or 0,
        stdout or '',
        stderr or '',
        retcode == 0,
        retcode != 0,
    ))

    return patch('peltak.core.shell.run', p_run)


def patch_open(module: str, read_data: str = '', create: bool = True) -> Any:
    """ Patch builtin open() function for the given module

    This is a convenient wrapper around mock_open.
    """
    return patch(
        module + '.open',
        create=create,
        new_callable=mock_open,
        read_data=read_data,
    )
