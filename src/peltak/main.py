# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# local imports
from peltak.core import conf
from peltak.commands import cli
__all__ = [
    'cli'
]


conf.load()


try:
    # Only enabled click_completion if psutil package is installed
    import psutil
    import click_completion
    click_completion.init()
except ImportError:
    pass


from peltak.commands import clean
from peltak.commands import git
