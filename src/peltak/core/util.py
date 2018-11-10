# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
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
""" Various helpers that do not depend on anything else in the project. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import re
import time
import warnings
from functools import wraps
from types import FunctionType
from typing import Any, Dict, Generator, Iterable, List, Text, TextIO, Union

# 3rd party imports
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


TextOrStream = Union[Text, TextIO]
YamlData = Union[Dict[Text, Any], List[Any]]


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


def mark_experimental(fn):
    # type: (FunctionType) -> FunctionType
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
                          "without notice within with a patch version update. "
                          "Use at your own risk")
        return fn(*args, **kw)

    return wrapper


def mark_deprecated(replaced_by):
    # type: (Text) -> FunctionType
    """ Mark command as deprecated.

    Args:
        replaced_by (str):
            The command that deprecated this command and should be used instead.
    """
    def decorator(fn):   # pylint: disable=missing-docstring
        @wraps(fn)
        def wrapper(*args, **kw):   # pylint: disable=missing-docstring
            from peltak.core import shell

            if shell.is_tty:
                warnings.warn("This command is has been deprecated. Please use "
                              "{new} instead.".format(new=replaced_by))

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

    def __call__(self, fn):
        # type: (FunctionType) -> FunctionType
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
    def clear(cls, fn):
        # type: (FunctionType) -> None
        """ Clear result cache on the given function.

        If the function has no cached result, this call will do nothing.

        Args:
            fn (FunctionType):
                The function whose cache should be cleared.
        """
        if hasattr(fn, cls.CACHE_VAR):
            delattr(fn, cls.CACHE_VAR)


def in_batches(iterable, batch_size):
    # type: (Iterable[Any]) -> Generator[List[Any]]
    """ Split the given iterable into batches.

    Args:
        iterable (Iterable[Any]):
            The iterable you want to split into batches.
        batch_size (int):
            The size of each bach. The last batch will be probably smaller (if
            the number of elements cannot be equally divided.

    Returns:
        Generator[list[Any]]: Will yield all items in batches of **batch_size**
            size.

    Example:

        >>> from peltak.core import util
        >>>
        >>> batches = util.in_batches([1, 2, 3, 4, 5, 6, 7], 3)
        >>> batches = list(batches)     # so we can query for lenght
        >>> len(batches)
        3
        >>> batches
        [[1, 2, 3], [4, 5, 6], [7]]

    """
    items = list(iterable)
    size = len(items)

    for i in range(0, size, batch_size):
        yield items[i:min(i + batch_size, size)]


def yaml_load(str_or_fp):
    # type: (TextOrStream) -> YamlData
    """ Load data from YAML string or file-like object.

    Args:
        str_or_fp (Union[str, TextIO]):

    Returns:
        YamlData: The data loaded from the YAML string/file.
    """
    return yaml.load(str_or_fp, Loader=Loader)


def yaml_dump(data, stream=None):
    # type: (YamlData, Optional[TextIO]) -> Text
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


def remove_indent(text):
    # type: (Text) -> Text
    """ Remove indentation from the text.

    All indentation will be removed no matter if it's consistent across the
    *text*.

    Args:
        text (str): The text that contains indentation.

    Returns:
        str: The same text but with all indentation removed from each line.
    """
    return re.sub('\n[ \t]+', '\n', text.lstrip())


# Used in type hint comments only (until we drop python2 support)
del Any, Dict, FunctionType, Generator, Iterable, List, Text, TextIO, Union
