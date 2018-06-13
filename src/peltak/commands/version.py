# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# 3rd party modules
import click

# local imports
from peltak.core import log, conf, versioning
from . import cli


VERSION_FILE = conf.get_path('VERSION_FILE', 'VERSION')

@cli.group('version')
def ver():
    """ Versioning related commands. """
    pass


@ver.command('show')
def version():
    """ Return current project version. """
    current = versioning.current(VERSION_FILE)

    log.info("Version: ^35{}".format(current))


@ver.command('bump')
@click.argument('component', required=False, default='patch')
@click.option('--exact', type=str)
def bump_version(component='patch', exact=None):
    """ Bump current project version without committing anything.

    No tags are created either.
    """
    log.info("Bumping package version")

    old_ver = versioning.current(VERSION_FILE)
    log.info("  old version: ^35{}".format(old_ver))

    if versioning.is_valid(exact):
        new_ver = exact
    else:
        new_ver = versioning.bump(old_ver, component)

    with open(VERSION_FILE, 'w') as fp:
        fp.write(new_ver)

    log.info("  new version: ^35{}".format(new_ver))
