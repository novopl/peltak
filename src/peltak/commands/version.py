# -*- coding: utf-8 -*-
""" Commands for managing the managed project version. """
from __future__ import absolute_import, unicode_literals
from . import cli, click


@cli.group('version', invoke_without_command=True)
@click.option('--porcelain', is_flag=True)
@click.pass_context
def ver(ctx, porcelain):
    """ Show project version. Has subcommands. """
    if not ctx.invoked_subcommand:
        _show_version(porcelain)


@ver.command('show')
@click.option('--porcelain', is_flag=True)
def show(porcelain):
    """ Deprecated. Use ``peltak version``. """
    _show_version(porcelain)


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
    from peltak.core import log
    from peltak.core import versioning

    old_ver, new_ver = versioning.bump(component, exact)

    log.info("Bumping package version")
    log.info("  old version: <35>{}".format(old_ver))
    log.info("  new version: <35>{}".format(new_ver))


def _show_version(porcelain):
    from peltak.core import log
    from peltak.core import versioning
    current = versioning.current()

    if porcelain:
        print(current)
    else:
        log.info("Version: <35>{}".format(current))
