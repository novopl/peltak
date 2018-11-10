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
""" Commands for managing the managed project version. """
from __future__ import absolute_import

from . import root_cli, click, pretend_option


@root_cli.group('version', invoke_without_command=True)
@click.option('--porcelain', is_flag=True)
@click.pass_context
def version_cli(ctx, porcelain):
    # type: (click.Context, bool) -> None
    """ Show project version. Has sub commands.

    For this command to work you must specify where the project version is
    stored. You can do that with version_file conf variable. peltak supports
    multiple ways to store the project version. Right now you can store it in a
    python file using built-in __version__ variable. You can use node.js
    package.json and keep the version there or you can just use a plain text
    file that just holds the raw project version. The appropriate storage is
    guessed based on the file type and name.

    Example Configuration::

        version_file: 'src/mypackage/__init__.py'

    Examples:

        \b
        $ peltak version                        # Pretty print current version
        $ peltak version --porcelain            # Print version as raw string
        $ peltak version bump patch             # Bump patch version component
        $ peltak version bump minor             # Bump minor version component
        $ peltak version bump major             # Bump major version component
        $ peltak version bump release           # same as version bump patch
        $ peltak version bump --exact=1.2.1     # Set project version to 1.2.1

    """
    if ctx.invoked_subcommand:
        return

    from peltak.core import log
    from peltak.core import versioning

    current = versioning.current()

    if porcelain:
        print(current)
    else:
        log.info("Version: <35>{}".format(current))


@version_cli.command('bump')
@click.argument(
    'component',
    type=click.Choice(['major', 'minor', 'patch']),
    required=False,
    default='patch'
)
@click.option('--exact', type=str)
@pretend_option
def bump_version(component='patch', exact=None):
    # type: (str, str) -> None
    """ Bump current project version without committing anything.

    No tags are created either.

    Examples:

        \b
        $ peltak version bump patch             # Bump patch version component
        $ peltak version bump minor             # Bump minor version component
        $ peltak version bump major             # Bump major version component
        $ peltak version bump release           # same as version bump patch
        $ peltak version bump --exact=1.2.1     # Set project version to 1.2.1

    """
    from peltak.core import log
    from peltak.core import versioning

    old_ver, new_ver = versioning.bump(component, exact)

    log.info("Project version bumped")
    log.info("  old version: <35>{}".format(old_ver))
    log.info("  new version: <35>{}".format(new_ver))
