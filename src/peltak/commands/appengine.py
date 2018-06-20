# -*- coding: utf-8 -*-
"""
Commands related to Google AppEngine.

Only useful on appengine projects. If you're not using AppEngine, do not
import those into your fabfile.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
import os
import os.path

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import log
from peltak.core import shell
from . import cli


@cli.group()
def appengine():
    """ Google AppEngine related commands. """
    pass


@appengine.command()
@click.option('-p', '--port', type=int, default=8080)
@click.option('--admin-port', type=int, default=None)
@click.option('--clear', is_flag=True)
def devserver(port, admin_port, clear):
    """ Run devserver. """
    admin_port = admin_port or (port + 1)

    args = [
        '--port={}'.format(port),
        '--admin_port={}'.format(admin_port)
    ]

    if clear:
        args += ['--clear_datastore=yes']

    with conf.within_proj_dir():
        shell.run('dev_appserver.py . {args}'.format(args=' '.join(args)))


@appengine.command()
@click.option('-v', '--version', type=str, default='playground')
@click.option('--promote', is_flag=True)
def deploy(version, promote):
    """ Deploy to Google AppEngine. """
    with conf.within_proj_dir():
        args = [
            '-q',
            '--project=worclock',
            '--version={}'.format(version)
        ]

        if promote:
            args += ['--promote']
        else:
            args += ['--no-promote']

        shell.run('gcloud app deploy {} app.yaml '.format(' '.join(args)))


@appengine.command('setup-ci')
@click.argument('project', type=str)
def setup_ci(project):
    """ Setup AppEngine SDK on CircleCI """
    gcloud_path = shell.run('which gcloud', capture=True).stdout
    sdk_path = os.path.normpath(os.path.join(
        gcloud_path, '../../platform/google_appengine'
    ))
    gcloud_cmd = '/opt/google-cloud-sdk/bin/gcloud --quiet'

    if not os.path.exists(sdk_path):
        log.info("Installing AppEngine SDK")
        shell.run('sudo {} components install app-engine-python'.format(
            gcloud_cmd
        ))
    else:
        # Only initialise once. To reinitialise, just build without cache.
        log.info("AppEngine SDK already initialised")

    log.info("Using service account authentication")
    shell.run('{} auth activate-service-account --key-file {}'.format(
        gcloud_cmd,
        conf.proj_path('ops/client_secret.json')
    ))

    # shell.run('{} config set project {}'.format(gcloud_cmd, project))


def _is_appengine_sdk(path):
    """ Return True if the given *path* contains AppEngine SDK. """
    return all(os.path.exists(os.path.join(path, f)) for f in (
        'appcfg.py',
        'dev_appserver.py',
        'google',
        'lib',
    ))


def _get_appengine_sdk_path():
    sdk_path = os.environ.get('APPENGINE_SDK')

    if sdk_path is None:
        sdk_path = _find_appengine_sdk()

    if sdk_path is None:
        msg_lines = (
            '^91AppEngine SDK not found!^0',
            '^90m',
            '   The Google AppEngine SDK must be in your ^1$PATH^90 or you can'
            ' use  ^1$APPENGINE_SDK^90 environment variable to specify it'
            ' directly.',
            '^0'
        )
        log.cprint('\n'.join(msg_lines))
        sys.exit(1)

    return sdk_path


def _find_appengine_sdk():
    """ Find appengine_sdk in the current $PATH. """
    paths = sys.path + os.environ.get('PATH').split(':')
    return next((path for path in paths if _is_appengine_sdk(path)), None)
