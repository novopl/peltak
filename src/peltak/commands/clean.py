# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import
from . import cli, click


@cli.command()
def clean():
    """ Remove temporary files like python cache, swap files, etc. """
    import os
    from peltak.core import conf
    from peltak.core import fs

    cwd = os.getcwd()
    clean_patterns = conf.get('CLEAN_PATTERNS', [
        '__pycache__',
        '*.py[cod]',
        '.swp',
    ])

    os.chdir(conf.proj_path('.'))

    for pattern in clean_patterns:
        fs.rm_glob(pattern)

    os.chdir(cwd)


@cli.command()
def init():
    """ Create new peltak config file in the current directory """
    from os.path import exists
    from peltak.core import log
    from peltak.core import shell

    config_file = 'pelconf.py'
    prompt = "-- <35>{} <32>already exists. Wipe it?<0>".format(config_file)

    if exists(config_file) and not click.confirm(shell.fmt(prompt)):
        log.info("Canceled")
        return

    log.info('Writing <35>{}'.format(config_file))
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
