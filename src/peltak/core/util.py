# -*- coding: utf-8 -*-
""" Various helpers that do not depend on anything else in the project. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import time
import warnings
from functools import wraps


class timed_block(object):  # noqa
    """ Context manager to measure execution time for a give block of code.

    >>> import time
    >>> from peltak.core import util
    >>>
    >>> with util.timed_block() as t:
    ...     time.sleep(1)
    >>>
    >>> print("Code executed in {}s".format(int(t.elapsed_s)))
    Code executed in 1s

    """
    def __enter__(self):
        self.t0 = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.time() - self.t0
        self.elapsed_s = round(self.elapsed, 3)
        self.elapsed_ms = round(self.elapsed * 1000, 3)


def mark_experimental(fn):
    """ Mark function as experimental.

    :param Function fn:
        The command function to decorate.
    """
    @wraps(fn)
    def wrapper(*args, **kw):   # pylint: disable=missing-docstring
        warnings.warn("This command is has experimental status. The interface "
                      "is not yet stable and might change without notice "
                      "within with a patch version update. "
                      "Use at your own risk")
        return fn(*args, **kw)

    return wrapper


def mark_deprecated(replaced_by):
    """ Mark command as deprecated.

    :param str replaced_by:
        The command that deprecated this command and should be used instead.
    """
    def decorator(fn):   # pylint: disable=missing-docstring
        @wraps(fn)
        def wrapper(*args, **kw):   # pylint: disable=missing-docstring
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
        """ Apply the decorator to the given function.

        :param Function fn:
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
        """ Clear result cache on the given function.

        If the function has no cached result, this call will do nothing.

        :param Function fn:
            The function whose cache should be cleared.
        """
        if hasattr(fn, cls.CACHE_VAR):
            delattr(fn, cls.CACHE_VAR)
