# -*- coding: utf-8 -*-
""" Application entry point. """
# pylint: disable=unused-import
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.commands import root_cli
__all__ = [
    'root_cli'
]


conf.load()


from peltak.commands.root import clean   # noqa
