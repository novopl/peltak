# Copyright 2021 Mateusz Klos
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
from typing import List, Tuple

from peltak.cli import click, peltak_cli, verbose_option


# TODO: Add date filter.
#  It should be possible to only search for todos that are newer than <data>.
#  It should accept '2020-01-15', '2020-01' and '2020'
# TODO: Add granular definition for git files checked
#  Allow passing --staged `--unstaged`, `--changed`, (staged + unstaged), `--untracked` to
#  define which git files should be checked
# TODO: Support passing directory via --file argument
#  Should check all files in the given directory.
@peltak_cli.command('todos')
@click.option(
    '-a',
    '--author',
    'authors',
    type=str,
    multiple=True,
    default=None,
    help="Show only TODOs for a given author (can use multiple times to show for"
         "multiple authors)."
)
@click.option(
    '--verify-complete',
    is_flag=True,
    default=False,
    help="Return with non-zero exit code if there are any TODOs left in the code."
)
@click.argument(
    'input_paths',
    type=click.Path(exists=True, dir_okay=True, file_okay=True),
    required=True,
    nargs=-1,
)
@verbose_option
def todos(
    input_paths: Tuple[str, ...],
    authors: List[str],
    verify_complete: bool,
) -> None:
    """ Scan code for TODOs and print a report.

    INPUT_PATH argument also accepts few special tokens that map to files with a given
    git status. Those tokens are:

      :commit:      All the files that has been changed since the last commit.
                    Comprises of the currently staged and unstaged chanegs in git.
      :diff:        Will look for todos in the files that has changed between the current
                    branch and the master branch.
      :untracked:   Maps to all files untracked but not ignored files.

    Examples::

        \b
        $ peltak todos src tests
        $ peltak todos . --untracked
        $ peltak todos . --author novopl
        $ peltak . --verify-complete
    """
    from . import logic

    logic.check_todos(input_paths, authors, verify_complete)
