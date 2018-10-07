# -*- coding: utf-8 -*-
""" git flow release commands. """

# 3rd party imports
import click

# local imports
from peltak.cli.release import release_cli


@release_cli.command('start')
@click.option(
    '-c', '--component',
    type=click.Choice(['major', 'minor', 'patch']),
    required=False,
    default='patch',
    help=("Which version component to bump with this release.")
)
@click.option(
    '--exact',
    type=str,
    help="Set the newly released version to be exactly as specified."
)
def start(component, exact):
    """ Create a new release.

    :param str component:
        Version component to bump when creating the release. Can be *major*,
        *minor* or *patch*.
    :param str exact:
        The exact version to set for the release. Overrides the component
        argument. This allows to re-release a version if something went wrong
        with the release upload.
    """
    from peltak.extra.gitflow import commands
    commands.release.start(component, exact)


@release_cli.command('tag')
def tag_release():
    """ Tag the current commit with as the current version release.

    This should be the same commit as the one that's uploaded as the release
    (to pypi for example).

    **Example Config**::

        \b
        conf.init({
            'version_file': 'src/mypkg/__init__.py'
        })

    Examples::

        $ peltak release tag          # Tag the current commit as release

    """
    from peltak.extra.gitflow import commands
    commands.release.tag()


@release_cli.command('finish')
def finish():
    """ Merge the current release to both develop and master.

    This will perform a FF merge with develop if possible and --no-ff merge
    with master and then tag the merge commit with the current version.
    """
    from peltak.extra.gitflow import commands
    commands.release.finish()


@release_cli.command('merged')
def merged():
    """ Checkout the target branch, pull and delete the merged branch.

    This is to ease the repetitive cleanup of each merged branch.

    Example Config (those the are defaults)::

        \b
        conf.init({
            'main_branch': 'develop',
            'master_branch': 'master',
            'protected_branches': ['master', 'develop'],
            'release_branch_pattern: 'release/*'
        })

    Example::

        $ peltak release merged     # Must be ran on the relase branch

    """
    from peltak.extra.gitflow import commands
    commands.release.merged()
