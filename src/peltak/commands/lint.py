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
""" Code linting commands. """
from __future__ import absolute_import

from typing import List

# local imports
from peltak.core import conf
from . import root_cli, click, pretend_option, verbose_option


conf.command_requirements(
    'pylint==1.9.2',
    'pep8==1.7.0',
)


@root_cli.group('lint', invoke_without_command=True)
@click.option(
    '-e', '--exclude',
    multiple=True,
    metavar='PATTERN',
    help=("Specify patterns to exclude from linting. For multiple patterns, "
          "use the --exclude option multiple times")
)
@click.option(
    '--skip-untracked',
    is_flag=True,
    help="Also include files not tracked by git."
)
@click.option(
    '--commit', 'commit_only',
    is_flag=True,
    help=("Only lint files staged for commit. Useful if you want to clean up "
          "a large code base one commit at a time.")
)
@pretend_option
@verbose_option
@click.pass_context
def lint_cli(ctx, exclude, skip_untracked, commit_only):
    # type: (click.Context, List[str], bool, bool) -> None
    """ Run pep8 and pylint on all project files.

    You can configure the linting paths using the lint.paths config variable.
    This should be a list of paths that will be linted. If a path to a directory
    is given, all files in that directory and it's subdirectories will be
    used.

    The pep8 and pylint config paths are by default stored in ops/tools/pep8.ini
    and ops/tools/pylint.ini. You can customise those paths in your config with
    lint.pep8_cfg and lint.pylint_cfg variables.

    **Config Example**::

        \b
        lint:
          pylint_cfg: 'ops/tools/pylint.ini'
          pep8_cfg: 'ops/tools/pep8.ini'
          paths:
            - 'src/mypkg'

    **Examples**::

        \b
        $ peltak lint               # Run linter in default mode, skip untracked
        $ peltak lint --commit      # Lint only files staged for commit
        $ peltak lint --all         # Lint all files, including untracked.
        $ peltak lint --pretend     # Print the list of files to lint
        $ peltak lint -e "*.tox*"   # Don't lint files inside .tox directory

    """
    if ctx.invoked_subcommand:
        return

    from peltak.logic import lint
    lint.lint(exclude, skip_untracked, commit_only)


# Used in docstrings only until we drop python2 support
del List
