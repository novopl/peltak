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
##############
``peltak git``
##############

git helpers.
"""
from peltak.commands import click, root_cli, pretend_option


@root_cli.group('git')
def git_cli():
    """ Git related commands """
    pass


@git_cli.command('add-hooks')
@pretend_option
@click.option(
    '--pre-commit',
    type=str,
    prompt='Pre commit tool',
    help=(
        'Command that will be ran before every commit. If it fails, the commit '
        'will fail.'
    )
)
@click.option(
    '--pre-push',
    type=str,
    prompt='Pre push tool',
    help=(
        'Command that will be ran before every push. If it fails, the push '
        'will fail.'
    )
)
def add_hooks(pre_commit: str, pre_push: str):
    """ Setup project git hooks.

    This will run all the checks before pushing to avoid waiting for the CI
    fail.

    Example::

        $ peltak git add-hooks

    """
    from . import impl

    impl.add_hooks(pre_commit, pre_push)


@git_cli.command('push')
@pretend_option
def push():
    """ Push the current branch and set to track remote.

    Example::

        $ peltak git push --pretend
        $ peltak git push

    """
    from . import impl
    impl.push()


@git_cli.command('delete-remote')
@pretend_option
def delete_remote():
    """ Delete the current branch on remote origin.

    This is an equivalent of ``git push origin :<branch>``. Easy way to quickly
    delete the remote branch without having to type in the branch name.

    Example::

        $ peltak git delete-remote --pretend
        $ peltak git delete-remote

    """
    from . import impl
    impl.push()
