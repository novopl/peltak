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
""" git flow hotfix commands. """
from peltak.commands import root_cli, click, pretend_option


@root_cli.group('hotfix', invoke_without_command=True)
def hotfix_cli():
    # type: () -> None
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
def start(name):
    # type: (str) -> None
    """ Start a new git flow hotfix branch.  """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Hotfix name')

    logic.hotfix.start(name)


@hotfix_cli.command('rename')
@click.argument('name', required=False)
@pretend_option
def rename(name):
    # type: (str) -> None
    """ Give the currently developed hotfix a new name. """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Hotfix name')

    logic.hotfix.rename(name)


@hotfix_cli.command('update')
@pretend_option
def update():
    # type: () -> None
    """ Update the hotfix with updates committed to master. """
    from peltak.extra.gitflow import logic
    logic.hotfix.update()


@hotfix_cli.command('finish')
@pretend_option
def finish():
    # type: () -> None
    """ Merge current hotfix into master. """
    from peltak.extra.gitflow import logic
    logic.hotfix.finish()


@hotfix_cli.command('merged')
@pretend_option
def merged():
    # type: () -> None
    """ Cleanup a remotely merged hotfix. """
    from peltak.extra.gitflow import logic
    logic.hotfix.merged()
