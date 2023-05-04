# Copyright 2017-2023 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
.. module:: peltak.core.util
    :synopsis: Various helpers that do not depend on anything else in the project.
"""
import re
import time
import warnings
from functools import wraps
from pprint import pformat
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Text,
    TextIO,
    Union,
)

import tomlkit
import yaml


try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader  # type: ignore


TextOrStream = Union[Text, TextIO]
PlainDict = Dict[str, Any]
YamlData = Union[PlainDict, List[Any]]
AnyFunction = Callable[..., Any]
Decorator = Callable[[AnyFunction], AnyFunction]


class timed_block(object):  # noqa
    """ Context manager to measure execution time for a give block of code.

    Example:
        >>> import time
        >>> from peltak.core import util
        >>>
        >>> with util.timed_block() as t:
        ...     time.sleep(1)
        >>>
        >>> print("Code executed in {}s".format(int(t.elapsed_s)))
        Code executed in 1s

    Attributes:
        t0 (float):
            The time at the start of execution.
        elapsed (float);
            Raw elapsed time in seconds.
        elapsed_s (float):
            Elapsed time in seconds, rounded to 3 decimal places for easy
            display.
        elapsed_ms (float):
            Elapsed time in milliseconds, rounded to 3 decimal places for easy
            display.
    """
    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.t0
        self.elapsed_s = round(self.elapsed, 3)
        self.elapsed_ms = round(self.elapsed * 1000, 3)


def mark_experimental(fn: AnyFunction) -> AnyFunction:
    """ Mark function as experimental.

    Args:
        fn (FunctionType):
            The command function to decorate.
    """
    @wraps(fn)
    def wrapper(*args, **kw):   # pylint: disable=missing-docstring
        from peltak.core import shell

        if shell.is_tty:
            warnings.warn("This command is has experimental status. The "
                          "interface is not yet stable and might change "
                          "without notice. Use at your own risk")
        return fn(*args, **kw)

    return wrapper


def mark_deprecated(replaced_by: str) -> Decorator:
    """ Mark command as deprecated.

    Args:
        replaced_by:
            The command that deprecated this command and should be used instead.
    """
    def decorator(fn):   # pylint: disable=missing-docstring
        @wraps(fn)
        def wrapper(*args, **kw):   # pylint: disable=missing-docstring
            from peltak.core import shell

            if shell.is_tty:
                warnings.warn("This command is has been deprecated. Please use "
                              "'{new}' instead.".format(new=replaced_by))

            return fn(*args, **kw)

        return wrapper

    return decorator


class cached_result(object):
    """ Decorator that caches the function result.

    This is especially useful for functions whose output won't change during
    a single *peltak* execution run and are expensive (i.e. call external
    shell commands).

    Example:
        >>> from peltak.core import util
        >>>
        >>> @util.cached_result()
        ... def foo():
        ...     call_count = getattr(foo, 'call_count', 0)
        ...     call_count += 1
        ...     setattr(foo, 'call_count', call_count)
        >>> foo()
        >>> print(foo.call_count)
        1
        >>> foo()
        >>> print(foo.call_count)
        1
        >>> util.cached_result.clear(foo)
        >>> foo()
        >>> print(foo.call_count)
        2
    """
    CACHE_VAR = '__cached_result'

    def __init__(self):
        pass

    def __call__(self, fn: AnyFunction) -> AnyFunction:
        """ Apply the decorator to the given function.

        Args:
            fn (FunctionType):
                The function to decorate.
        :return Function:
            The function wrapped in caching logic.
        """
        @wraps(fn)
        def wrapper(refresh=False):   # pylint: disable=missing-docstring
            if refresh or not hasattr(wrapper, self.CACHE_VAR):
                result = fn()
                setattr(wrapper, self.CACHE_VAR, result)

            return getattr(wrapper, self.CACHE_VAR)

        return wrapper

    @classmethod
    def clear(cls, fn: AnyFunction):
        """ Clear result cache on the given function.

        If the function has no cached result, this call will do nothing.

        Args:
            fn (FunctionType):
                The function whose cache should be cleared.
        """
        if hasattr(fn, cls.CACHE_VAR):
            delattr(fn, cls.CACHE_VAR)


def in_batches(iterable: Iterable[Any], batch_size: int) -> Iterator[List[Any]]:
    """ Split the given iterable into batches.

    Args:
        iterable (Iterable[Any]):
            The iterable you want to split into batches.
        batch_size (int):
            The size of each bach. The last batch will be probably smaller (if
            the number of elements cannot be equally divided.

    Returns:
        Iterator[list[Any]]: Will yield all items in batches of **batch_size**
            size.

    Example:

        >>> from peltak.core import util
        >>>
        >>> batches = util.in_batches([1, 2, 3, 4, 5, 6, 7], 3)
        >>> batches = list(batches)     # so we can query for length
        >>> len(batches)
        3
        >>> batches
        [[1, 2, 3], [4, 5, 6], [7]]

    """
    items = list(iterable)
    size = len(items)

    for i in range(0, size, batch_size):
        yield items[i:min(i + batch_size, size)]


def yaml_load(str_or_fp: TextOrStream) -> YamlData:
    """ Load data from YAML string or file-like object.

    Args:
        str_or_fp (Union[str, TextIO]):

    Returns:
        YamlData: The data loaded from the YAML string/file.
    """
    return yaml.load(str_or_fp, Loader=Loader)


def yaml_dump(data: YamlData, stream: Optional[Any] = None) -> Text:
    """ Dump data to a YAML string/file.

    Args:
        data (YamlData):
            The data to serialize as YAML.
        stream (TextIO):
            The file-like object to save to. If given, this function will write
            the resulting YAML to that stream.

    Returns:
        str: The YAML string.
    """
    return yaml.dump(
        data,
        stream=stream,
        Dumper=Dumper,
        default_flow_style=False
    )


def toml_load(path_or_fp: TextOrStream) -> PlainDict:
    """ Load TOML configuration into a dict. """
    if isinstance(path_or_fp, str):
        with open(path_or_fp) as fp:
            document = tomlkit.parse(fp.read())
            return dict(document)
    else:
        document = tomlkit.parse(path_or_fp.read())
        return dict(document)


def toml_dump(data: PlainDict, path_or_fp: Optional[TextOrStream] = None):
    """ Save a plain dict as a TOML file. """
    document = tomlkit.item(data)
    if path_or_fp is None:
        return tomlkit.dumps(document)
    elif isinstance(path_or_fp, str):
        with open(path_or_fp, 'w') as fp:
            fp.write(tomlkit.dumps(document))

    else:
        path_or_fp.write(tomlkit.dumps(document))


def remove_indent(text: str) -> str:
    """ Remove indentation from the text.

    All indentation will be removed no matter if it's consistent across the
    *text*.

    Args:
        text (str): The text that contains indentation.

    Returns:
        str: The same text but with all indentation removed from each line.
    """
    return re.sub('\n[ \t]+', '\n', text.lstrip())


class Singleton(object):
    """ Base class for singletons.

    Inheriting from this class will make your class a singleton. It should have
    an initializer that takes no arguments.
    """
    instances: Dict[str, Any] = {}

    def __new__(cls, *args, **kw):
        # Could upgrade this to thread local storage
        instance = Singleton.instances.get(cls.__name__)

        if instance:
            instance._singleton_initialized = True
        else:
            instance = object.__new__(cls)
            instance._singleton_initialized = False
            Singleton.instances[cls.__name__] = instance

        return instance


def get_from_dict(dct: Dict, path: str, *default: Any) -> Any:
    """ Get value from dictionary using a dotted path.

    This allows you to get a value from deep within a dictionary without having
    to manually check at each level if the key exists and handling the default
    properly. This function will work the same as dict.get() but allows you to
    specify a path in dotted notation, eg: 'main.sub.value'. Depending on whether
    you passed a default value it will either return it or raise KeyError
    if any of the keys or value itself is missing.

    Args:
        dct:
            The dict the requested value will be read from.
        path:
            The name/path of the config value.
        *default:
            If given and the key doesn't not exist, this will be returned
            instead. If it's not given and the config value does not exist,
            KeyError will be raised.

    Returns:
        The requested config value. This is one of the global values defined
        in this file. If the value does not exist it will return *default* if
        give or raise `AttributeError`.

    Raises:
        KeyError: If the value does not exist and *default* was not given.

    Examples:
        >>> d = {
        ...     'main': {
        ...         'value': 123,
        ...     }
        ... }
        ...
        >>> get_from_dict(d, 'main.value')
        123
        >>> get_from_dict(d, 'missing', 321)
        321
        >>> get_from_dict(d, 'missing')
        Traceback (most recent call last):
        KeyError:
    """
    curr = dct
    for part in path.split('.'):
        if part in curr:
            curr = curr[part]
        elif default:
            return default[0]
        else:
            raise KeyError(f"'{path}' not found in dict: {pformat(dct)}")

    return curr


def set_in_dict(dct: Dict, path: str, value: Any) -> None:
    """ Set value in a dictionary using a dotted path.

    This is the opposite to `get_from_dict()` function, but sets the value under
    the given path instead.


    Args:
        dct:
            The dict that will be modified by this call.
        path:
            The name/path of the context value to change.
        value:
            The new value for the selected context value

    Raises:
        KeyError: If the value does not exist and *default* was not given.

    Examples:
        >>> d = {
        ...     'main': {
        ...         'value': 123,
        ...     }
        ... }
        ...
        >>> set_in_dict(d, 'main.value', 321)
        >>> d
        {'main': {'value': 321}}

    """
    curr = dct
    parts = path.split('.')

    for i, part in enumerate(parts[:-1]):
        try:
            curr = curr.setdefault(part, {})
        except AttributeError:
            raise KeyError('.'.join(parts[:i + 1]))

    try:
        curr[parts[-1]] = value
    except TypeError:
        raise KeyError('.'.join(parts[:-1]))


def dict_has(dct: Dict, path: str) -> bool:
    """ Check if a given dict has a value under a comma separated name/path.

    This will split *path* by dots and drill down the dictionary to check if the value
    exists.
    """
    curr = dct
    for part in path.split('.'):
        if part in curr:
            curr = curr[part]
        else:
            return False

    return True
