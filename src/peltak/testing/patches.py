""" A place to store all patch functions specific to peltak.

Easier to track them down, when you need one.
"""
from functools import wraps
from typing import Any, Dict, Optional
from unittest.mock import Mock, mock_open, patch

from peltak.core.shell import ExecResult

from peltak.core import shell


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
    """ Overwrite the project root path in Pelconf singleton. """
    from peltak.core import conf

    def decorator(fn):  # pylint: disable=missing-docstring
        @wraps(fn)
        def wrapper(*args, **kw):  # pylint: disable=missing-docstring
            current_proj_root = conf.proj_root_path
            conf.proj_root_path = path

            result = fn(*args, **kw)

            conf.proj_root_path = current_proj_root
            return result

        return wrapper
    return decorator


def patch_pelconf(config: Dict[str, Any]) -> Any:
    """ Patch the peltak configuration.

    This will patch all content retrieved through `peltak.core.conf.get()` and
    `conf.get_path()`.

    Args:
        config (dict[str, Any]):
            The dictionary with the peltak configuration.
    """
    return patch('peltak.core.conf.values', config)


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
