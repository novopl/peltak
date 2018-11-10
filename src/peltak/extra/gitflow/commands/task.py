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
""" git flow feature commands. """
from peltak.commands import root_cli, click, pretend_option


@root_cli.group('task', invoke_without_command=True)
def task_cli():
    # type: () -> None
    """ Start a new git-flow task.

    Tasks can only be based on feature branches.
    """
    pass


@task_cli.command('start')
@click.argument('name', required=False)
@pretend_option
def start(name):
    # type: (str) -> None
    """ Start a new git-flow feature.  """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Task name')

    logic.task.start(name)


@task_cli.command('rename')
@click.argument('name', required=False)
@pretend_option
def rename(name):
    # type: (str) -> None
    """ Give the currently developed feature a new name. """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Task name')

    logic.task.rename(name)


@task_cli.command('update')
@pretend_option
def update():
    # type: () -> None
    """ Update the feature with updates committed to develop. """
    from peltak.extra.gitflow import logic
    logic.task.update()


@task_cli.command('finish')
@pretend_option
def finish():
    # type: () -> None
    """ Merge current feature into develop. """
    from peltak.extra.gitflow import logic
    logic.task.finish()


@task_cli.command('merged')
@pretend_option
def merged():
    # type: () -> None
    """ Cleanup a remotely merged branch. """
    from peltak.extra.gitflow import logic
    logic.task.merged()
