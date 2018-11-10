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
""" Commands related to Google AppEngine.

Only useful on appengine projects.
"""
from __future__ import absolute_import

from peltak.commands import root_cli, click, pretend_option


@root_cli.group('appengine')
def appengine_cli():
    # type: () -> None
    """ Google AppEngine related commands. """
    pass


@appengine_cli.command('deploy')
@click.option(
    '--project',
    type=str,
    metavar='APP_ID',
    help=("The AppEngine project to deploy to. This overrides the value "
          "configured using appengine.projects config variable.")
)
@click.option(
    '--version',
    type=str,
    metavar='APP_VERSION',
    help=("The AppEngine version to deploy. This overrides the value "
          "configured using appengine.projects config variable.")
)
@click.option(
    '--promote',
    is_flag=True,
    help=("If specified, the currently deployed version will become the active "
          "one")
)
@click.option(
    '-q', '--quiet',
    is_flag=True,
    help="Do not prompt for input"
)
@pretend_option
def deploy(project, version, promote, quiet):
    """ Deploy the app to the target environment.

    The target environments can be configured using the ENVIRONMENTS conf
    variable. This will also collect all static files and compile translation
    messages
    """
    from . import logic

    logic.deploy(project, version, promote, quiet)


@appengine_cli.command()
@click.option('-p', '--port', type=int, default=8080)
@click.option('--admin-port', type=int, default=None)
@click.option('--clear', is_flag=True)
@pretend_option
def devserver(port, admin_port, clear):
    # type: (int, int, bool) -> None
    """ Run devserver. """
    from . import logic

    logic.devserver(port, admin_port, clear)


@appengine_cli.command('setup-ci')
@pretend_option
def setup_ci():
    # type: () -> None
    """ Setup AppEngine SDK on CircleCI """
    from . import logic

    logic.setup_ci()
