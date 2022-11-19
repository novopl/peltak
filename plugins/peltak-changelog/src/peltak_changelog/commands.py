# Copyright 2017-2021 Mateusz Klos
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
"""
####################
``peltak changelog``
####################

CLI definition.
"""

from peltak.cli import click, peltak_cli


@peltak_cli.group(
    'changelog',
    invoke_without_command=True,
    help=(
        "Generate changelog from commit messages.\n"
        "\n"
        "This will go over all commits between the given git revisions and"
        "extract all changelog data from them. If called without arguments "
        "it will show all changelog entries since the last version tag."
    )
)
@click.option(
    '-s', '--start-rev',
    help="Starting revision. Defaults to last version tag found"
)
@click.option(
    '-e', '--end-rev',
    help='End revision, defaults to HEAD',
)
@click.option(
    '-t', '--title',
    default=None,
    help=(
        'Changelog title.\n'
        '\n'
        'Will use the current project version if not given. Use empty string '
        'to remove the title completely, ie `peltak changelog --title ""`'
    ),
)
@click.pass_context
def changelog_cli(ctx: click.Context, start_rev: str, end_rev: str, title: str) -> None:
    """ Generate changelog from commit messages. """
    if ctx.invoked_subcommand:
        return

    from peltak.core import shell

    from . import logic

    changelog = logic.changelog(start_rev=start_rev, end_rev=end_rev, title=title)
    shell.cprint(changelog)
