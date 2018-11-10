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
""" AppEngine commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import itertools
import sys
from fnmatch import fnmatch
from os.path import exists, join, normpath
from typing import Optional

# 3rd party imports
import attr

# local imports
from peltak.core import conf
from peltak.core import context
from peltak.core import fs
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from peltak.core import versioning
from peltak.core import util


@util.mark_experimental
def deploy(app_id, version, promote, quiet):
    # type: (str, str, bool, bool) -> None
    """ Deploy the app to AppEngine.

    Args:
        app_id (str):
            AppEngine App ID. Overrides config value app_id if given.
        version (str):
            AppEngine project version. Overrides config values if given.
        promote (bool):
            If set to **True** promote the current remote app version to the one
            that's being deployed.
        quiet (bool):
            If set to **True** this will pass the ``--quiet`` flag to gcloud
            command.
    """
    gae_app = GaeApp.for_branch(git.current_branch().name)

    if gae_app is None and None in (app_id,  version):
        msg = (
            "Can't find an AppEngine app setup for branch <35>{}<32> and"
            "--project and --version were not given."
        )
        log.err(msg, git.current_branch().name)
        sys.exit(1)

    if version is not None:
        gae_app.version = version

    if app_id is not None:
        gae_app.app_id = app_id

    gae_app.deploy(promote, quiet)


@util.mark_experimental
def devserver(port, admin_port, clear):
    # type: (int, int, bool) -> None
    """ Run devserver.

    Args:
        port (int):
            Port on which the app will be served.
        admin_port (int):
            Port on which the admin interface is served.
        clear (bool):
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
def setup_ci():
    # type: () -> None
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
    # type: () -> str
    gcloud_path = shell.run('which gcloud', capture=True).stdout.strip()
    return normpath(join(gcloud_path, '../../platform/google_appengine'))


@attr.s
class GaeApp(object):
    """ Represents an AppEngine app.

    Attributes:
        app_id (str):
            AppEngine project ID.
        version (str):
            AppEngine project version.
        deployables (list[str]):
            List of YAML files to deploy. Defaults to all yaml files in the
            project root directory.
    """
    app_id = attr.ib(type=str)
    version = attr.ib(type=str, default=None)
    deployables = attr.ib(type=list, default=['.'])

    @classmethod
    def for_branch(cls, branch_name):
        # type: (str) -> Optional[GaeApp]
        """ Return app configuration for the given branch.

        This will look for the configuration in the ``appengine.projects``
        config variable.

        Args:
            branch_name (str):
                The name of the branch we want the configuration for.

        Returns:
            Optional[GaeApp]: The `GaeApp` instance with the configuration for
                the project.
            None: If no project configuration can be found.
        """
        for proj in conf.get('appengine.projects', []):
            if fnmatch(branch_name, proj['branch']):
                proj = dict(proj)
                proj.pop('branch')
                proj['deployables'] = list(frozenset(itertools.chain(
                    conf.get('appengine.deployables', []),
                    proj.get('deployables', [])
                )))
                return cls(**proj)

        return None

    @property
    def app_version(self):
        # type: () -> str
        """ AppEngine compatible app version.

        This assumes git-flow branching strategy and has a few predefined ways
        to automatically generate the version string.
        """
        branch = git.current_branch()

        if self.version is not None:
            return self.version

        elif branch.type == 'develop':
            return '{ver}-c{commit_nr}-{commit_id}'.format(
                ver=versioning.current().replace('.', '-'),
                commit_nr=git.latest_commit().number,
                commit_id=git.latest_commit().id
            )

        elif branch.type in ('feature', 'hotfix', 'task'):
            # We don't need version when we have the title.
            return branch.title.replace('_', '-')

        return versioning.current().replace('.', '-')

    def deploy(self, promote=False, quiet=False):
        # type: (bool, bool, bool) -> None
        """ Deploy the code to AppEngine.

        Args:
            promote (bool):
                Migrate the traffic to the deployed version.
            quiet (bool):
                Pass ``--quiet`` flag to gcloud command
        """
        args = [
            '--promote' if promote else '--no-promote',
            '--version {}'.format(self.app_version),
            '--project {}'.format(self.app_id),
        ]

        if quiet:
            args += ['--quiet']

        cmd = 'gcloud app deploy {args} {deployables}'.format(
            deployables=fs.wrap_paths(self.deployables),
            args=' '.join(args)
        )

        if context.get('pretend', False):
            log.info("Would deploy version <35>{ver}<32> to <35>{app}".format(
                ver=self.app_version,
                app=self.app_id
            ))
            shell.cprint('<90>{}', cmd)
        else:
            log.info("Deploying version <35>{ver}<32> to <35>{app}".format(
                ver=self.app_version,
                app=self.app_id,
            ))
            shell.run(cmd)


# Used in type hint comments only (until we drop python2 support)
del Optional
