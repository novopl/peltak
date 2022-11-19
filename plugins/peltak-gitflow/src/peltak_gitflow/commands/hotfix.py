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
"""
#################
``peltak hotfix``
#################
"""
from peltak.cli import click, peltak_cli, pretend_option


@peltak_cli.group('hotfix', invoke_without_command=True)
def hotfix_cli():
    """ Commands that ease the work with git flow hotfix branches.

    Examples:

        \b
        $ peltak hotfix start my_hotfix     # Start a new hotfix branch
        $ peltak hotfix finish              # Merge the hotfix into master
        $ peltak hotfix merged              # Cleanup after a remote merge
        $ peltak hotfix rename new_name     # Rename the current hotfix.
    """
    pass


@hotfix_cli.command('start')
@click.argument('name', required=False)
@pretend_option
def start(name: str):
    """ Start a new git flow hotfix branch.  """
    from peltak_gitflow import logic

    if name is None:
        name = click.prompt('Hotfix name')

    logic.hotfix.start(name)


@hotfix_cli.command('rename')
@click.argument('name', required=False)
@pretend_option
def rename(name: str):
    """ Give the currently developed hotfix a new name. """
    from peltak_gitflow import logic

    if name is None:
        name = click.prompt('Hotfix name')

    logic.hotfix.rename(name)


@hotfix_cli.command('update')
@pretend_option
def update():
    """ Update the hotfix with updates committed to master. """
    from peltak_gitflow import logic
    logic.hotfix.update()


@hotfix_cli.command('finish')
@pretend_option
@click.option(
    '--ff', '--fast-forward', 'fast_forward',
    is_flag=True,
    help="Try to perform a fast-forward merge. If possible this will not "
         "create a merge commit on the target branch."
)
def finish(fast_forward: bool):
    """ Merge current hotfix into master. """
    from peltak_gitflow import logic
    logic.hotfix.finish(fast_forward)


@hotfix_cli.command('merged')
@pretend_option
def merged():
    """ Cleanup a remotely merged hotfix. """
    from peltak_gitflow import logic
    logic.hotfix.merged()
