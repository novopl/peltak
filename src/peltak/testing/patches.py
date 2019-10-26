# -*- coding: utf-8 -*-
""" A place to store all patch functions specific to peltak.

Easier to track them down, when you need one.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from functools import wraps
from os.path import join
from typing import Any, Dict

# 3rd party imports
from mock import patch, Mock
from peltak.core.shell import ExecResult

# local imports
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


class patch_proj_root(object):
    """ Patch project root decorator. """
    def __init__(self, proj_root, nest_level=0):
        self.proj_root = proj_root
        self.nest = nest_level

    def __call__(self, fn):
        if self.proj_root is not None:
            cwd = join(self.proj_root, *(['fake_dir'] * self.nest))
            dirs = ['not_pelconf'] * self.nest + ['pelconf.py']
            dirs = [[d] for d in dirs]
        else:
            cwd = join('/', *(['fake_dir'] * self.nest))
            dirs = [[d] for d in ['not_pelconf'] * self.nest]

        @patch('os.getcwd', Mock(return_value=cwd))
        @patch('os.listdir', Mock(side_effect=dirs))
        @wraps(fn)
        def wrapper(*args, **kw):       # pylint: disable=missing-docstring
            return fn(*args, **kw)

        return wrapper


def patch_pelconf(config):
    # type: (Dict[str, Any]) -> Any
    """ Patch the peltak configuration.

    This will patch all content retrieved through `peltak.core.conf.get()` and
    `conf.get_path()`.

    Args:
        config (dict[str, Any]):
            The dictionary with the peltak configuration.
    """
    return patch('peltak.core.conf.values', config)


def patch_run(stdout=None, retcode=None, stderr=None, cmd=None):
    # type: (str, int, str, str) -> Any
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


# Used only in type hint comments
del Any, Dict
