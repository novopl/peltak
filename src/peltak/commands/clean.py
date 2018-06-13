# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os

# local imports
from peltak.core import conf
from peltak.core import fs
from . import cli


CLEAN_PATTERNS = conf.get('CLEAN_PATTERNS', [
    '__pycache__',
    '*.py[cod]',
    '.swp',
])


@cli.command()
def clean():
    """ Remove temporary files like python cache, swap files, etc. """
    cwd = os.getcwd()

    os.chdir(conf.proj_path('.'))

    for pattern in CLEAN_PATTERNS:
        fs.rm_glob(pattern)

    os.chdir(cwd)
