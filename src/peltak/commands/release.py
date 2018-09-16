# -*- coding: utf-8 -*-
""" Helper commands for releasing to pypi. """
from __future__ import absolute_import
from . import cli, click


@cli.group('release', invoke_without_command=True)
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
@click.pass_context
def release_cli(ctx, component, exact):
    """ Create a new release branch.

    It will bump the current version number and create a release branch called
    `release/<version>` with one new commit (the version bump).

    **Example Config**::

        \b
        conf.init({
            'version_file': 'src/mypkg/__init__.py'
        })

    **Examples**::

        \b
        $ peltak release --component=patch    # Make a new patch release
        $ peltak release -c minor             # Make a new minor release
        $ peltak release -c major             # Make a new major release
        $ peltak release                      # same as release -c patch
        $ peltak release tag                  # Tag current commit as release
        $ peltak release upload pypi          # Upload to pypi

    """
    if ctx.invoked_subcommand:
        return

    from .impl import release
    release.release(component, exact)


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
    from .impl import release
    release.tag_release()


@release_cli.command()
@click.argument('target')
def upload(target):
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak release upload pypi    # Upload the current release to pypi
        $ peltak release upload private # Upload to pypi server 'private'

    """
    from .impl import release
    release.upload(target)


@release_cli.command('gen-pypirc')
@click.argument('username', required=False)
@click.argument('password', required=False)
def gen_pypirc(username=None, password=None):
    """
    Generate .pypirc config with the given credentials.

    Example::

        $ peltak release gen-pypirc my_pypi_user my_pypi_pass

    """
    from .impl import release
    release.gen_pypirc(username, password)


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
    from .impl import release
    release.merged()
