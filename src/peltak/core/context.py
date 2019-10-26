# -*- coding: utf-8 -*-
""" Runtime context implementation.

.. module:: peltak.core.context
    :synopsis: Runtime context for peltak commands.


Runtime context is a unified place to store dynamic global configuration. The
verbosity and ``pretend`` is a good example of that.

Works like `peltak.core.pelconf` but the configuration can be dynamically modified
in runtime.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any, Text

# local imports
from . import util


class ContextError(Exception):
    """ Base class for context related exceptions. """
    pass


class InvalidPath(ContextError):
    """ Invalid variable path. """
    def __init__(self, path):
        super(InvalidPath, self).__init__("{} is not a dict".format(
            '.'.join(path)
        ))


class RunContext(util.Singleton):
    """ Runtime context.

    This class is the equivalent of conf but for values that can be modified
    in runtime. This is for all the settings that can be set on the command
    line and can span many commands or APIs.
    """

    def __init__(self):
        # __init__ can be called multiple times since this class is a singleton
        if not self._singleton_initialized:
            self.values = {}

    def clear(self):
        # type: () -> None
        """ Clear all existing values. """
        self.values = {}

    def get(self, name, *default):
        # type: (str, Any) -> Any
        """ Get context value with the given name and optional default.

        Args:
            name (str):
                The name of the context value.
            *default (Any):
                If given and the key doesn't not exist, this will be returned
                instead. If it's not given and the context value does not exist,
                `AttributeError` will be raised

        Returns:
            The requested context value.  If the value does not exist it will
            return *default* if give or raise `AttributeError`.

        Raises:
            AttributeError: If the value does not exist and *default* was not
                given.
        """

        curr = self.values
        for part in name.split('.'):
            if part in curr:
                curr = curr[part]
            elif default:
                return default[0]
            else:
                fmt = "Context value '{}' does not exist:\n{}"
                raise AttributeError(fmt.format(
                    name, util.yaml_dump(self.values)
                ))

        return curr

    def set(self, name, value):
        """ Set context value.

        Args:
            name (str):
                The name of the context value to change.
            value (Any):
                The new value for the selected context value
        """
        curr = self.values
        parts = name.split('.')

        for i, part in enumerate(parts[:-1]):
            try:
                curr = curr.setdefault(part, {})
            except AttributeError:
                raise InvalidPath('.'.join(parts[:i + 1]))

        try:
            curr[parts[-1]] = value
        except TypeError:
            raise InvalidPath('.'.join(parts[:-1]))


def get(name, *default):
    # type: (Text, *Any) -> Any
    """ Get context value with the given name and optional default.

    Args:
        name (str):
            The name of the context value.
        *default (Any):
            If given and the key doesn't not exist, this will be returned
            instead. If it's not given and the context value does not exist,
            `AttributeError` will be raised

    Returns:
        The requested context value.  If the value does not exist it will
        return *default* if give or raise `AttributeError`.

    Raises:
        AttributeError: If the value does not exist and *default* was not
            given.
    """
    return RunContext().get(name, *default)


def set(name, value):   # pylint: disable=redefined-builtin
    # type: (Text, Any) -> None
    """ Set context value.

    Args:
        name (str):
            The name of the context value to change.
        value (Any):
            The new value for the selected context value
    """
    RunContext().set(name, value)


def clear():
    # type: () -> None
    """ Clear all existing values. """
    return RunContext().clear()


# Used in type hints comments only (until we drop python2 support)
del Any, Text
