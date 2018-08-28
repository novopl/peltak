# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import
from . import cli, click


@cli.command('clean')
@click.option(
    '-p', '--pretend',
    is_flag=True,
    help=("Just print files that would be deleted, without actually "
          "deleting them")
)
@click.option(
    '-e', '--exclude',
    multiple=True,
    metavar='PATTERN',
    help='Comma separated list of paths to exclude from deletion'
)
def clean(pretend, exclude):
    """ Remove temporary files like python cache, swap files, etc.

    You can configure the list of patterns with CLEAN_PATTERNS config variable.
    By default it will remove all files/dirs matching

    Config example::

        \b
        conf.init({
            'CLEAN_PATTERNS': [
                '*__pycache__*',
                '*.py[cod]',
                '*.swp'
        })

    Examples::

        \b
        $ peltak clean
        $ peltak clean -e "*.tox*"
        $ peltak clean --pretend

    """
    import os
    from os.path import isdir
    from shutil import rmtree
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import log

    clean_patterns = conf.get('CLEAN_PATTERNS', [
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


@cli.command('init')
def init():
    """ Create new peltak config file in the current directory.

    If ``pelconf.py`` already exists the user will be prompted to confirm
    before continuing.

    Example::

        $ peltak init

    """
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
