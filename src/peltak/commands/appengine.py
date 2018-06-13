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
from fabric.api import lcd, local

# local imports
from .common import conf
from .common import log


def devserver(port='8080', admin_port=None, clear='False'):
    """ Run devserver. """
    clear = conf.is_true(clear)
    port = int(port)
    admin_port = admin_port or (port + 1)

    args = [
        '--port={}'.format(port),
        '--admin_port={}'.format(admin_port)
    ]

    if clear:
        args += ['--clear_datastore=yes']

    with lcd(conf.proj_path()):
        local('dev_appserver.py . {args}'.format(args=' '.join(args)))


def deploy(version='playground', promote='false'):
    """ Deploy to Google AppEngine. """
    with lcd(conf.proj_path()):
        args = [
            '-q',
            '--project=worclock',
            '--version={}'.format(version)
        ]

        if conf.is_true(promote):
            args += ['--promote']
        else:
            args += ['--no-promote']

        local('gcloud app deploy {} app.yaml '.format(' '.join(args)))


def appengine_ci_setup(project):
    """ Setup AppEngine SDK on CircleCI """
    gcloud_path = local('which gcloud', capture=True).stdout
    sdk_path = os.path.normpath(os.path.join(
        gcloud_path, '../../platform/google_appengine'
    ))
    gcloud_cmd = '/opt/google-cloud-sdk/bin/gcloud --quiet'

    if not os.path.exists(sdk_path):
        log.info("Installing AppEngine SDK")
        local('sudo {} components install app-engine-python'.format(gcloud_cmd))
    else:
        # Only initialise once. To reinitialise, just build without cache.
        log.info("AppEngine SDK already initialised")

    log.info("Using service account authentication")
    local('{} auth activate-service-account --key-file {}'.format(
        gcloud_cmd,
        conf.proj_path('ops/client_secret.json')
    ))

    # local('{} config set project {}'.format(gcloud_cmd, project))


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
