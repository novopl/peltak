# -*- coding: utf-8 -*-
""" Root level CLI commands. """
from __future__ import absolute_import

# stdlib imports
from typing import List

# local imports
from . import root_cli, click


@root_cli.command('clean')
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
    # type: (bool, List[str]) -> None
    """ Remove temporary files like python cache, swap files, etc.

    You can configure the list of patterns with clean_patterns config variable.
    By default it will remove all files/dirs matching

    Config example::

        \b
        clean:
          patterns:
            - '*__pycache__*',
            - '*.py[cod]',
            - '*.swp'
          exclude:
            - '.tox'
            - '.venv'

    Examples::

        \b
        $ peltak clean
        $ peltak clean -e "*.tox*"
        $ peltak clean --pretend

    """
    from peltak.commands import root
    root.clean(pretend, exclude)


@root_cli.command('init')
def init():
    # type: () -> None
    """ Create new peltak config file in the current directory.

    If ``pelconf.py`` already exists the user will be prompted to confirm
    before continuing.

    Example::

        $ peltak init

    """
    from peltak.commands import root
    root.init()


# Used in docstrings only until we drop python2 support
del List
