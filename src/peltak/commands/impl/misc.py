# -*- coding: utf-8 -*-
""" Miscellaneous commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import exists, isdir
from shutil import rmtree

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import fs
from peltak.core import log
from peltak.core import shell


def clean(pretend, exclude):
    """ Remove all unnecessary files.

    :param bool pretend:
        If set to **True**, do not delete any files, just show what would be
        deleted.
    :param List[str] exclude:
        A list of path patterns to exclude from deletion.
    """
    clean_patterns = conf.get('clean_patterns', [
        '*__pycache__*',
        '*.py[cod]',
        '*.swp',
    ])

    files = fs.filtered_walk(conf.proj_path(), clean_patterns, exclude)

    for path in files:
        try:
            if not isdir(path):
                log.info('  <91>[file] <90>{}', path)
                if not pretend:
                    os.remove(path)
            else:
                log.info('  <91>[dir]  <90>{}', path)
                if not pretend:
                    rmtree(path)
        except OSError:
            log.info("<33>Failed to remove <90>{}", path)


def init():
    """ Create an empty pelconf.py from template """
    config_file = 'pelconf.py'
    prompt = "-- <35>{} <32>already exists. Wipe it?<0>".format(config_file)

    if exists(config_file) and not click.confirm(shell.fmt(prompt)):
        log.info("Canceled")
        return

    log.info('Writing <35>{}'.format(config_file))
    with open('pelconf.py', 'w') as fp:
        fp.write('''# -*- coding: utf-8 -*-
""" peltak configuration file.

See https://github.com/novopl/peltak for more information.
"""
from __future__ import absolute_import

# Configure the build
from peltak.core import conf

conf.init({
})

# Import all commands
#from peltak.commands import version
''')
