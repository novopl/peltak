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
from peltak.core import util


@util.mark_experimental
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


@util.mark_experimental
def deploy(project, version, pretend, promote, deploy_all):
    """ Deploy the app to AppEngine.

    :param str project:
        AppEngine project ID. Overrides config values if given.
    :param str version:
        AppEngine project version. Overrides config values if given.
    :param bool pretend:
        If set to **True**, do not actually deploy anything but show the deploy
        command that would be used.
    :param bool promote:
        If set to **True** promote the current remote app version to the one
        that's being deployed.
    :param bool deploy_all:
    :return:
    """
    gae_projects = conf.get('appengine.projects')
    branch = git.branch_details()
    gae_proj = next(
        (e for e in gae_projects if fnmatch(branch.name, e['branch'])),
        None
    )
    args = []

    if gae_proj is None:
        log.err("Can't find an GAE project setup for branch <35>{}", branch)
        sys.exit(1)

    if promote:
        args += ['--promote']
    else:
        args += ['--no-promote']

    if version is not None:
        app_version = version
    elif branch.type == 'feature':
        app_version = '{ver}-{title}'.format(
            ver=versioning.current().replace('.', '-'),
            title=branch.title.replace('_', '-')
        )
    else:
        app_version = versioning.current().replace('.', '-')

    app_id = project or gae_proj.get('name')
    args += [
        '--version {}'.format(app_version),
        '--project {}'.format(app_id),
    ]

    deployables = [gae_proj['config']]

    if deploy_all:
        deployables += conf.get('appengine.deployables', [
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
            log.info("Would deploy version <35>{ver} <32>to <35>{proj}".format(
                ver=app_version,
                proj=gae_proj['name']
            ))
            shell.cprint('<90>{}', cmd)

        if not pretend:
            log.info("Deploying version <35>{ver} <32>to <35>{proj}".format(
                ver=app_version,
                proj=gae_proj['name']
            ))
            shell.run(cmd)


@util.mark_experimental
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
