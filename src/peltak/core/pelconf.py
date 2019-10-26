# -*- coding: utf-8 -*-
"""
.. module:: peltak.core.pelconf
    :synopsis: `pelconf.yaml` handling.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import os.path
import sys
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Dict, Iterator, List, Optional, Text, Union

# local imports
from . import hooks
from . import log
from . import util


class Pelconf(util.Singleton):
    """ Represents the `pelconf.yaml` file. """
    def __init__(self):
        if not self._singleton_initialized:
            self.values = {}    # type: Dict[str, Any]

    def from_file(self, path):
        """ Load config values from a YAML file. """
        with self.within_proj_dir():
            with open(path) as fp:
                self.values = util.yaml_load(fp) or {}

    def reset(self, config):
        """ Reset config to the given values.

        This will completely overwrite the current configuration.
        """
        self.values = config

    @classmethod
    def init(cls):
        ""
        cfg = cls()
        cfg.values = {}
        if os.path.exists('pelconf.yaml'):
            cfg.from_file('pelconf.yaml')

        # Add src_dir to sys.paths if it's set. This is only done with YAML
        # configs, py configs have to do this manually.
        src_dir = cfg.get_path('src_dir', None)
        if src_dir is not None:
            sys.path.insert(0, src_dir)

        for cmd in cfg.get('commands', []):
            try:
                _import(cmd)
            except ImportError as ex:
                log.err("Failed to load commands from <33>{}<31>: {}", cmd, ex)

        hooks.register.call('post-conf-load')

    def get(self, name, *default):
        # type: (str, *Any) -> Any
        """ Get config value with the given name and optional default.

        Args:
            name (str):
                The name of the config value.
            *default (Any):
                If given and the key doesn't not exist, this will be returned
                instead. If it's not given and the config value does not exist,
                AttributeError will be raised

        Returns:
            The requested config value. This is one of the global values defined
            in this file. If the value does not exist it will return *default* if
            give or raise `AttributeError`.

        Raises:
            AttributeError: If the value does not exist and *default* was not given.
        """
        curr = self.values
        for part in name.split('.'):
            if part in curr:
                curr = curr[part]
            elif default:
                return default[0]
            else:
                raise AttributeError("Config value '{}' does not exist".format(
                    name
                ))

        return curr

    def get_path(self, name, *default):
        # type: (str, Any) -> Any
        """ Get config value as path relative to the project directory.

        This allows easily defining the project configuration within the fabfile
        as always relative to that fabfile.

        Args:
            name (str):
                The name of the config value containing the path.
            *default (Any):
                If given and the key doesn't not exist, this will be returned
                instead. If it's not given and the config value does not exist,
                AttributeError will be raised

        Returns:
            The requested config value. This is one of the global values defined
            in this file. If the value does not exist it will return *default* if
            give or raise `AttributeError`.

        Raises:
            AttributeError: If the value does not exist and *default* was not given.
        """
        value = self.get(name, *default)

        if value is None:
            return None

        return self.proj_path(value)

    def get_env(self, name, *default):
        # type: (str, Any) -> Union[str, Any]
        """ Get the value of an ENV variable. """
        return os.environ.get(name, *default)

    def proj_path(self, *path_parts):
        # type: (*str) -> str
        """ Return absolute path to the repo dir (root project directory).

        Args:
            path (str):
                The path relative to the project root (pelconf.yaml).

        Returns:
            str: The given path converted to an absolute path.
        """
        parts = list(path_parts) or ['.']

        # If path represented by path_parts is absolute, do not modify it.
        if not os.path.isabs(parts[0]):
            proj_path = _find_proj_root()

            if proj_path is not None:
                parts = [proj_path] + list(parts)

        return os.path.normpath(os.path.join(*parts))

    @contextmanager
    def within_proj_dir(self, path='.'):
        # type: (str) -> Iterator[None]
        """ Return an absolute path to the given project relative path.

        :param path:
            Project relative path that will be converted to the system wide absolute
            path.
        :return:
            Absolute path.
        """
        curr_dir = os.getcwd()

        os.chdir(self.proj_path(path))

        yield

        os.chdir(curr_dir)


@util.cached_result()
def _find_proj_root():
    # type: () -> Optional[str]
    """ Find the project path by going up the file tree.

    This will look in the current directory and upwards for the pelconf file
    (.yaml or .py)
    """
    proj_files = frozenset(('pelconf.py', 'pelconf.yaml'))
    curr = os.getcwd()

    while curr.startswith('/') and len(curr) > 1:
        if proj_files & frozenset(os.listdir(curr)):
            return curr
        else:
            curr = os.path.dirname(curr)

    return None


def _import(cmd):
    # type: (str) -> ModuleType
    """ Exists only so we can patch it in tests."""
    return __import__(cmd)   # nocov


# Used in type hint comments only (until we drop python2 support)
del Any, Dict, Iterator, List, Optional, Union, Text, ModuleType
