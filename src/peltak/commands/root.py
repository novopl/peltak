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
from . import root_cli, click, pretend_option


@root_cli.command('clean')
@click.option(
    '-e', '--exclude',
    multiple=True,
    metavar='PATTERN',
    help='Comma separated list of paths to exclude from deletion'
)
@pretend_option
def clean(exclude):
    # type: (List[str]) -> None
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
    root.clean(exclude)


@root_cli.command('init')
@click.option(
    '-q', '--quick',
    is_flag=True,
    help="Enable quick mode. Defaults will be used wherever possible."
)
@pretend_option
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


@root_cli.command('devrequirements')
def project_dev_requirements():
    """ List requirements for peltak commands configured for the project.

    This list is dynamic and depends on the commands you have configured in
    your project's pelconf.yaml. This will be the combined list of packages
    needed to be installed in order for all the configured commands to work.
    """
    from peltak.core import conf
    from peltak.core import shell

    for dep in sorted(conf.requirements):
        shell.cprint(dep)


# Used in docstrings only until we drop python2 support
del List
