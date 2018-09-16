# -*- coding: utf-8 -*-
""" Commands package.

All commands (and only commands) should be defined inside this package. This
should be as thin layer as possible. Ideally just processing CLI params and
displaying results.
"""
from __future__ import absolute_import

# 3rd party imports
import click

import peltak


@click.group()
@click.version_option(version=peltak.__version__, message='%(version)s')
def cli():
    """

    To get help for a specific command:

        \033[1mpeltak <command> --help\033[0m

    Examples:

        \033[1mpeltak lint --help\033[0m

        \033[1mpeltak version bump --help\033[0m

        \033[1mpeltak release upload --help\033[0m

    """
    pass


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

    You can configure the list of patterns with clean_patterns config variable.
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
    from .impl.misc import clean

    clean(pretend, exclude)


@cli.command('init')
def init():
    """ Create new peltak config file in the current directory.

    If ``pelconf.py`` already exists the user will be prompted to confirm
    before continuing.

    Example::

        $ peltak init

    """
    from .impl.misc import init

    init()
