# Copyright 2017-2020 Mateusz Klos
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
from typing import Any, List

from . import click, peltak_cli, pretend_option, verbose_option


@peltak_cli.command('clean')
@click.option(
    '-e', '--exclude',
    multiple=True,
    metavar='PATTERN',
    help='Comma separated list of paths to exclude from deletion'
)
@pretend_option
@verbose_option
def clean(exclude: List[str]) -> None:
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
    from . import peltak_impl
    peltak_impl.clean(exclude)


@peltak_cli.command('init')
@click.option(
    '-q', '--quick',
    is_flag=True,
    help="Enable quick mode. Defaults will be used wherever possible."
)
@click.option(
    '-b', '--blank',
    is_flag=True,
    help="Create a blank configuration without asking any questions."
)
@click.option(
    '-f', '--force',
    is_flag=True,
    help="Force creating. This will not ask whether to wipe out existing config"
         "or cancel in case the config already exists."
)
@click.option(
    '-t', '--template',
    type=click.Choice(['py', 'js']),
    default='py',
    help="Specify which template to use, defaults to python."
)
@pretend_option
@verbose_option
def init(**args: Any) -> None:
    """ Create new peltak config file in the current directory.

    If ``pelconf.py`` already exists the user will be prompted to confirm
    before continuing.

    Example::

        $ peltak init

    """
    from . import peltak_impl
    peltak_impl.init(**args)
