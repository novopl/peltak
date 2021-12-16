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
from typing import List, Optional

from peltak.commands import click, root_cli, verbose_option


# TODO: Add date filter.
#  It should be possible to only search for todos that are newer than <data>.
#  It should accept '2020-01-15', '2020-01' and '2020'
# TODO: Add granular definition for git files checked
#  Allow passing --staged `--unstaged`, `--changed`, (staged + unstaged), `--untracked` to
#  define which git files should be checked
# TODO: Support passing directory via --file argument
#  Should check all files in the given directory.
@root_cli.command('todos')
@click.option('-u', '--untracked', is_flag=True, default=False)
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
@click.option(
    '-f', '--file', 'file_path',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    default=None,
    help="Check just the given file."
)
@verbose_option
def todos(
    untracked: bool,
    file_path: Optional[str],
    authors: List[str],
    verify_complete: bool,
) -> None:
    """ Scan code for TODOs and print a report.

    Examples::

        \b
        $ peltak todos
        $ peltak todos --untracked
        $ peltak todos --author novopl
        $ peltak --verify-complete
    """
    from . import logic

    logic.check_todos(untracked, file_path, authors, verify_complete)
