# -*- coding: utf-8 -*-
""" Commands related to Google AppEngine.

Only useful on appengine projects. If you're not using AppEngine, do not
import inside `pelconf.py`.
"""
from __future__ import absolute_import
from . import cli, click


@cli.group('appengine')
def appengine_cli():
    """ Google AppEngine related commands. """
    pass


@appengine_cli.command('deploy')
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
    '--all', 'deploy_all',
    is_flag=True,
    help=("If specified, the command will deploy all deployables, and not only "
          "the app file. If you don't specify it, the command will only deploy "
          "app.yaml (for the given env ofc). ")
)
def deploy(pretend, promote, deploy_all):
    """ Deploy the app to the target environment.

    The target environments can be configured using the ENVIRONMENTS conf
    variable. This will also collect all static files and compile translation
    messages
    """
    from .impl.appengine import devserver

    devserver(pretend, promote, deploy_all)


@appengine_cli.command()
@click.option('-p', '--port', type=int, default=8080)
@click.option('--admin-port', type=int, default=None)
@click.option('--clear', is_flag=True)
def devserver(port, admin_port, clear):
    """ Run devserver. """
    from .impl.appengine import devserver

    devserver(port, admin_port, clear)


@appengine_cli.command('setup-ci')
def setup_ci():
    """ Setup AppEngine SDK on CircleCI """
    from .impl.appengine import setup_ci

    setup_ci()
