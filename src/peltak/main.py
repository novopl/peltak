# -*- coding: utf-8 -*-
""" Application entry point. """
# pylint: disable=unused-import
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.cli import cli
__all__ = [
    'cli'
]


conf.load()


from peltak.cli import clean   # noqa
