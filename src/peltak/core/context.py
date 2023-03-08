""" Runtime context implementation.

.. module:: peltak.core.context
    :synopsis: Runtime context for peltak commands.


Runtime context is a unified place to store dynamic global configuration. The
verbosity and ``pretend`` is a good example of that.

Works like `peltak.core.conf` but the configuration can be dynamically modified
in runtime.
"""
from typing import Any

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

    def clear(self) -> None:
        """ Clear all existing values. """
        self.values = {}

    def get(self, name: str, *default: Any) -> Any:
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
        try:
            return util.get_from_dict(self.values, name, *default)
        except KeyError:
            raise AttributeError(
                f"Context value '{name}' does not exist:\n{util.yaml_dump(self.values)}"
            )

    def has(self, name: str) -> bool:
        """ Check whether the given name/path is present in the context.

        Args:
            name:   The name of the value to check for. You can reach nested values using
                    the dot notation. For example ``some.value.name`` will internally
                    traverse up to 3 dictionaries to perform ths check.

        Returns:
            **True** if the value is stored in the context, **False** otherwise.
        """
        return util.dict_has(self.values, name)

    def set(self, name: str, value: Any) -> None:
        """ Set context value.

        Args:
            name (str):
                The name of the context value to change.
            value (Any):
                The new value for the selected context value
        """
        try:
            util.set_in_dict(self.values, name, value)
        except KeyError:
            raise InvalidPath(name)


def has(name: str) -> bool:
    """ Check whether the given name/path is present in the context.

    Args:
        name:   The name of the value to check for. You can reach nested values using
                the dot notation. For example ``some.value.name`` will internally
                traverse up to 3 dictionaries to perform ths check.

    Returns:
        **True** if the value is stored in the context, **False** otherwise.
    """
    return RunContext().has(name)


def get(name: str, *default: Any) -> Any:
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


def set(name: str, value: Any) -> None:   # pylint: disable=redefined-builtin
    """ Set context value.

    Args:
        name (str):
            The name of the context value to change.
        value (Any):
            The new value for the selected context value
    """
    RunContext().set(name, value)


def clear() -> None:
    """ Clear all existing values. """
    return RunContext().clear()
