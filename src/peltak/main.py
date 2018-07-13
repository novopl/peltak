# -*- coding: utf-8 -*-
""" Application entry point. """
# pylint: disable=unused-import
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.commands import cli
__all__ = [
    'cli'
]


conf.load()


try:
    # Only enable click_completion if psutil (shell auto detection) is present.
    import psutil
    import click_completion
    click_completion.init()
except ImportError:
    pass


from peltak.commands import clean   # noqa
