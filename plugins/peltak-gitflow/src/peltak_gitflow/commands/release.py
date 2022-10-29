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
``peltak release``
##################
git flow release commands.
"""
from peltak.cli import click, peltak_cli, pretend_option


@peltak_cli.group('release', invoke_without_command=True)
def release_cli():
    """ Commands that implement the release git flow.

    **Example Config**::

        \b
        version:
            file: 'src/mypkg/__init__.py'
        git:
            devel_branch: 'develop'
            master_branch: 'master'
            protected_branches: ['master', 'develop']

    Examples:

        \b
        $ peltak release start patch    # Make a new patch release
        $ peltak release start minor    # Make a new minor release
        $ peltak release start major    # Make a new major release
        $ peltak release start          # same as start patch
        $ peltak release tag            # Tag current commit as release

    """
    pass


@release_cli.command('start')
@click.argument(
    'component',
    type=click.Choice(['major', 'minor', 'patch']),
    default='patch',
)
@click.option(
    '--exact',
    type=str,
    help="Set the newly released version to be exactly as specified."
)
@pretend_option
def start(component: str, exact: str):
    """ Create a new release.

    It will bump the current version number and create a release branch called
    `release/<version>` with one new commit (the version bump).

    **Example Config**::

        \b
        version:
            file: 'src/mypkg/__init__.py'

    **Examples**::

        \b
        $ peltak release start patch    # Make a new patch release
        $ peltak release start minor    # Make a new minor release
        $ peltak release start major    # Make a new major release
        $ peltak release start          # same as start patch

    """
    from peltak_gitflow import logic
    logic.release.start(component, exact)


@release_cli.command('tag')
@click.option(
    '-m', '--message',
    type=str,
    help=("Tag message. Will replace the default 'Mark vX.X release'")
)
@pretend_option
def tag_release(message: str):
    """ Tag the current commit with as the current version release.

    This should be the same commit as the one that's uploaded as the release
    (to pypi for example).

    **Example Config**::

        \b
        version:
            file: 'src/mypkg/__init__.py'

    Examples::

        $ peltak release tag          # Tag the current commit as release

    """
    from peltak_gitflow import logic
    logic.release.tag(message)


@release_cli.command('finish')
@pretend_option
@click.option(
    '--ff', '--fast-forward', 'fast_forward',
    is_flag=True,
    help="Try to perform a fast-forward merge. If possible this will not "
         "create a merge commit on the target branch."
)
def finish(fast_forward: bool):
    """ Merge the current release to both develop and master.

    This will perform a FF merge with develop if possible and --no-ff merge
    with master and then tag the merge commit with the current version.
    """
    from peltak_gitflow import logic
    logic.release.finish(fast_forward)


@release_cli.command('merged')
@pretend_option
def merged():
    """ Checkout the target branch, pull and delete the merged branch.

    This is to ease the repetitive cleanup of each merged branch.

    Example Config (those the are defaults)::

        \b
        git:
            devel_branch: 'develop'
            master_branch: 'master'
            protected_branches: ['master', 'develop']

    Example::

        $ peltak release merged     # Must be ran on the relase branch

    """
    from peltak_gitflow import logic
    logic.release.merged()
