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
##################
``peltak feature``
##################

git flow feature commands.
"""
from peltak.cli import click, peltak_cli, pretend_option


@peltak_cli.group('feature', invoke_without_command=True)
def feature_cli():
    """ Start a new git-flow feature.  """


@feature_cli.command('start')
@click.argument('name', required=False)
@pretend_option
def start(name: str):
    """ Start a new git-flow feature.  """
    from peltak_gitflow import logic

    if name is None:
        name = click.prompt('Feature name')

    logic.feature.start(name)


@feature_cli.command('rename')
@click.argument('name', required=False)
@pretend_option
def rename(name: str):
    """ Give the currently developed feature a new name. """
    from peltak_gitflow import logic

    if name is None:
        name = click.prompt('Feature name')

    logic.feature.rename(name)


@feature_cli.command('update')
@pretend_option
def update():
    """ Update the feature with updates committed to develop. """
    from peltak_gitflow import logic
    logic.feature.update()


@feature_cli.command('finish')
@pretend_option
@click.option(
    '--ff', '--fast-forward', 'fast_forward',
    is_flag=True,
    help="Try to perform a fast-forward merge. If possible this will not "
         "create a merge commit on the target branch."
)
def finish(fast_forward: bool):
    """ Merge current feature into develop. """
    from peltak_gitflow import logic
    logic.feature.finish(fast_forward)


@feature_cli.command('merged')
@pretend_option
def merged():
    """ Cleanup a remotely merged branch. """
    from peltak_gitflow import logic
    logic.feature.merged()
