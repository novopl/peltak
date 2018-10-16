# -*- coding: utf-8 -*-
""" Commands related to Google AppEngine.

Only useful on appengine projects. If you're not using AppEngine, do not
import inside `pelconf.py`.
"""
from __future__ import absolute_import

from peltak.cli import cli, click


@cli.group('appengine')
def appengine_cli():
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
    '--pretend',
    is_flag=True,
    help=("Do not actually deploy to AppEngine.This will only collect all "
          "static files and compile i18n messages and tell you where the "
          "app would be deployed and what version would that be. Locally this "
          "is the same as just running the command but no changes will be done "
          "to the remote deployment.")
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
def deploy(project, version, pretend, promote, quiet):
    """ Deploy the app to the target environment.

    The target environments can be configured using the ENVIRONMENTS conf
    variable. This will also collect all static files and compile translation
    messages
    """
    from . import impl

    impl.deploy(project, version, pretend, promote, quiet)


@appengine_cli.command()
@click.option('-p', '--port', type=int, default=8080)
@click.option('--admin-port', type=int, default=None)
@click.option('--clear', is_flag=True)
def devserver(port, admin_port, clear):
    """ Run devserver. """
    from . import impl

    impl.devserver(port, admin_port, clear)


@appengine_cli.command('setup-ci')
def setup_ci():
    """ Setup AppEngine SDK on CircleCI """
    from . import impl

    impl.setup_ci()
