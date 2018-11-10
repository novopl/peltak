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
""" git flow release commands. """
from peltak.commands import root_cli, click, pretend_option


@root_cli.group('release', invoke_without_command=True)
def release_cli():
    # type: () -> None
    """ Commands that implement the release git flow.

    **Example Config**::

        \b
        version_file: 'src/mypkg/__init__.py'
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
def start(component, exact):
    # type: (str) -> None
    """ Create a new release.

    It will bump the current version number and create a release branch called
    `release/<version>` with one new commit (the version bump).

    **Example Config**::

        \b
        version_file: 'src/mypkg/__init__.py'

    **Examples**::

        \b
        $ peltak release start patch    # Make a new patch release
        $ peltak release start minor    # Make a new minor release
        $ peltak release start major    # Make a new major release
        $ peltak release start          # same as start patch

    """
    from peltak.extra.gitflow import logic
    logic.release.start(component, exact)


@release_cli.command('tag')
@click.option(
    '-m', '--message',
    type=str,
    help=("Tag message. Will replace the default 'Mark vX.X release'")
)
@pretend_option
def tag_release(message):
    # type: (str, bool) -> None
    """ Tag the current commit with as the current version release.

    This should be the same commit as the one that's uploaded as the release
    (to pypi for example).

    **Example Config**::

        \b
        version_file: 'src/mypkg/__init__.py'

    Examples::

        $ peltak release tag          # Tag the current commit as release

    """
    from peltak.extra.gitflow import logic
    logic.release.tag(message)


@release_cli.command('finish')
@pretend_option
def finish():
    # type: () -> None
    """ Merge the current release to both develop and master.

    This will perform a FF merge with develop if possible and --no-ff merge
    with master and then tag the merge commit with the current version.
    """
    from peltak.extra.gitflow import logic
    logic.release.finish()


@release_cli.command('merged')
@pretend_option
def merged():
    # type: () -> None
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
    from peltak.extra.gitflow import logic
    logic.release.merged()
