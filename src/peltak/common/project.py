# -*- coding: utf-8 -*-
"""
Project related helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from contextlib import contextmanager

# 3rd party imports
from fabric.api import lcd, quiet as fabric_quiet

# local imports
from . import conf


@contextmanager
def inside(path='.', quiet=False):
    """ Return absolute path to the repo dir (root project directory). """
    with lcd(conf.proj_path(path)):
        if quiet:
            with fabric_quiet():
                yield
        else:
            yield
