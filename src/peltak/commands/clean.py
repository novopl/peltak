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


@cli.command()
def init():
    """ Create new peltak config file in the current directory """
    with open('pelconf.py', 'w') as fp:
        fp.write('''# -*- coding: utf-8 -*-
""" peltak configuration file.

See `peltak <https://github.com/novopl/peltak>`_ for more information.
"""
from __future__ import absolute_import

# Configure the build
from peltak.core import conf

conf.init({
})

# Import all commands
#from peltak.commands import version
       ''')
