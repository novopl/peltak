# -*- coding: utf-8 -*-
""" Time related utilities. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import time
import warnings
from functools import wraps


class timed_block(object):  # noqa
    """ Context manager to measure execution time for a give block of code.

    .. code-block:: python

        with timed_block() as t:
            time.sleep(1)

        print("The block took {}ms to execute".format(t.elapsed_ms)
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
                      "is not yet stable and might change without notice and "
                      "with a minor version. Use at your own risk")
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
