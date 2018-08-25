# -*- coding: utf-8 -*-
""" Time related utilities. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import time


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
