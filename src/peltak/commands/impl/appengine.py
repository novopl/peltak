# -*- coding: utf-8 -*-
""" AppEngine commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import sys
from fnmatch import fnmatch
from os.path import exists, join, normpath

# local imports
from peltak.core import conf
from peltak.core import fs
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from peltak.core import versioning


def devserver(port, admin_port, clear):
    """ Run devserver.

    :param int port:
        Port on which the app will be served.
    :param int admin_port:
        Port on which the admin interface is served.
    :param bool clear:
        If set to **True**, clear the datastore on startup.
    """

    admin_port = admin_port or (port + 1)

    args = [
        '--port={}'.format(port),
        '--admin_port={}'.format(admin_port)
    ]

    if clear:
        args += ['--clear_datastore=yes']

    with conf.within_proj_dir():
        shell.run('dev_appserver.py . {args}'.format(args=' '.join(args)))


def deploy(pretend, promote, deploy_all):
    """ Deploy the app to AppEngine.

    :param bool pretend:
        If set to **True**, do not actually deploy anything but show the deply
        command that would be used.
    :param bool promote:
        If set to **True** promote the current remote app version to the one
        that's being deployed.
    :param bool deploy_all:
    :return:
    """
    environments = conf.get('APPENGINE_ENVS')
    branch = git.current_branch()
    env = next((e for e in environments if fnmatch(branch, e['branch'])), None)
    args = []
    deployables = []

    if env is None:
        log.err("Can't find an environment setup for branch <35>{}", branch)
        sys.exit(1)

    if promote:
        args += ['--promote']
    else:
        args += ['--no-promote']

    if branch.startswith('feature/'):
        app_version = '{ver}-{feature}'.format(
            ver=versioning.current().replace('.', '-'),
            feature=branch[8:].replace('_', '-')
        )
    else:
        app_version = versioning.current().replace('.', '-')

    args += [
        '--version {}'.format(app_version),
        '--project {}'.format(env['url']),
    ]

    deployables += [env['config']]

    if deploy_all:
        deployables += conf.get('APPENGINE_DEPLOYABLES', [
            'cron.yaml',
            'index.yaml',
            'queue.yaml',
        ])

    with conf.within_proj_dir():
        cmd = 'gcloud app deploy {args} {deployables}'.format(
            deployables=fs.surround_paths_with_quotes(deployables),
            args=' '.join(args)
        )

        if pretend:
            log.info("Would deploy version <35>{ver} <32>to <35>{url}".format(
                ver=app_version,
                url=env['url']
            ))
            shell.cprint('<90>{}', cmd)

        if not pretend:
            log.info("Deploying version <35>{ver} <32>to <35>{url}".format(
                ver=app_version,
                url=env['url']
            ))
            shell.run(cmd)


def setup_ci():
    """ Setup AppEngine SDK on CircleCI """
    gcloud_path = shell.run('which gcloud', capture=True).stdout.strip()
    sdk_path = normpath(join(gcloud_path, '../../platform/google_appengine'))
    gcloud_cmd = gcloud_path + ' --quiet'

    if not exists(sdk_path):
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


def _find_appengine_sdk():
    gcloud_path = shell.run('which gcloud', capture=True).stdout.strip()
    return normpath(join(gcloud_path, '../../platform/google_appengine'))
