# -*- coding: utf-8 -*-
""" Commands for managing the managed project version. """
from __future__ import absolute_import, unicode_literals

# 3rd party modules
import click

# local imports
from peltak.core import log
from peltak.core import versioning
from . import cli


@cli.group('version')
def ver():
    """ Versioning related commands. """
    pass


@ver.command('show')
@click.option('--porcelain', is_flag=True)
def version(porcelain):
    """ Return current project version. """
    current = versioning.current()

    if porcelain:
        print(current)
    else:
        log.info("Version: ^35{}".format(current))


@ver.command('bump')
@click.argument(
    'component',
    type=click.Choice(['major', 'minor', 'patch']),
    required=False,
    default='patch'
)
@click.option('--exact', type=str)
def bump_version(component='patch', exact=None):
    """ Bump current project version without committing anything.

    No tags are created either.
    """

    old_ver, new_ver = versioning.bump(component, exact)

    log.info("Bumping package version")
    log.info("  old version: ^35{}".format(old_ver))
    log.info("  new version: ^35{}".format(new_ver))
