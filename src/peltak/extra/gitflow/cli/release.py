# -*- coding: utf-8 -*-
""" git flow release commands. """
from peltak.cli import cli, click


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
    """ Create a new release.

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

    from peltak.extra.gitflow import impl
    impl.release.start(component, exact)


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
    from peltak.extra.gitflow import impl
    impl.release.tag()


@release_cli.command('finish')
def finish():
    """ Merge the current release to both develop and master.

    This will perform a FF merge with develop if possible and --no-ff merge
    with master and then tag the merge commit with the current version.
    """
    from peltak.extra.gitflow import impl
    impl.release.finish()


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
    from peltak.extra.gitflow import impl
    impl.release.merged()
