# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
    from peltak.logic import root
    root.clean(pretend, exclude)


@root_cli.command('init')
@click.option(
    '-q', '--quick',
    is_flag=True,
    help="Enable quick mode. Defaults will be used wherever possible."
)
def init(quick):
    # type: () -> None
    """ Create new peltak config file in the current directory.

    If ``pelconf.py`` already exists the user will be prompted to confirm
    before continuing.

    Example::

        $ peltak init

    """
    from peltak.logic import root
    root.init(quick)


# Used in docstrings only until we drop python2 support
del List
