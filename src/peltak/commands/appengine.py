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
    import sys
    from fnmatch import fnmatch
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import git
    from peltak.core import log
    from peltak.core import shell
    from peltak.core import versioning

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


@appengine_cli.command()
@click.option('-p', '--port', type=int, default=8080)
@click.option('--admin-port', type=int, default=None)
@click.option('--clear', is_flag=True)
def devserver(port, admin_port, clear):
    """ Run devserver. """
    from peltak.core import conf
    from peltak.core import shell

    admin_port = admin_port or (port + 1)

    args = [
        '--port={}'.format(port),
        '--admin_port={}'.format(admin_port)
    ]

    if clear:
        args += ['--clear_datastore=yes']

    with conf.within_proj_dir():
        shell.run('dev_appserver.py . {args}'.format(args=' '.join(args)))


@appengine_cli.command('setup-ci')
def setup_ci():
    """ Setup AppEngine SDK on CircleCI """
    import os.path
    from peltak.core import conf
    from peltak.core import log
    from peltak.core import shell

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
    import os.path

    return all(os.path.exists(os.path.join(path, f)) for f in (
        'appcfg.py',
        'dev_appserver.py',
        'google',
        'lib',
    ))


def _get_appengine_sdk_path():
    import sys
    import os.path
    from peltak.core import shell

    sdk_path = os.environ.get('APPENGINE_SDK')

    if sdk_path is None:
        sdk_path = _find_appengine_sdk()

    if sdk_path is None:
        msg_lines = (
            '<91>AppEngine SDK not found!<0>',
            '<90>',
            ' The Google AppEngine SDK must be in your <1>$PATH<90> or you can'
            ' use  <1>$APPENGINE_SDK<90> environment variable to specify it'
            ' directly.',
            '<0>'
        )
        shell.cprint('\n'.join(msg_lines))
        sys.exit(1)

    return sdk_path


def _find_appengine_sdk():
    """ Find appengine_sdk in the current $PATH. """
    import sys
    import os.path

    paths = sys.path + os.environ.get('PATH').split(':')
    return next((path for path in paths if _is_appengine_sdk(path)), None)
