# -*- coding: utf-8 -*-
""" git flow release commands. """
from peltak.cli import root_cli, click


@root_cli.group('release', invoke_without_command=True)
def release_cli():
    # type: () -> None
    """ Commands that implement the release git flow.

    **Example Config**::

        \b
        version_file: 'src/mypkg/__init__.py'
        git:
            devel_branch: 'develop'
            master_branch: 'master'
            protected_branches: ['master', 'develop']

    Examples:

        \b
        $ peltak release start patch    # Make a new patch release
        $ peltak release start minor    # Make a new minor release
        $ peltak release start major    # Make a new major release
        $ peltak release start          # same as start patch
        $ peltak release tag            # Tag current commit as release

    """
    pass


@release_cli.command('start')
@click.argument(
    'component',
    type=click.Choice(['major', 'minor', 'patch']),
    default='patch',
)
@click.option(
    '--exact',
    type=str,
    help="Set the newly released version to be exactly as specified."
)
def start(component, exact):
    # type: (str) -> None
    """ Create a new release.

    It will bump the current version number and create a release branch called
    `release/<version>` with one new commit (the version bump).

    **Example Config**::

        \b
        version_file: 'src/mypkg/__init__.py'

    **Examples**::

        \b
        $ peltak release start patch    # Make a new patch release
        $ peltak release start minor    # Make a new minor release
        $ peltak release start major    # Make a new major release
        $ peltak release start          # same as start patch

    """
    from peltak.extra.gitflow import logic
    logic.release.start(component, exact)


@release_cli.command('tag')
def tag_release():
    # type: () -> None
    """ Tag the current commit with as the current version release.

    This should be the same commit as the one that's uploaded as the release
    (to pypi for example).

    **Example Config**::

        \b
        version_file: 'src/mypkg/__init__.py'

    Examples::

        $ peltak release tag          # Tag the current commit as release

    """
    from peltak.extra.gitflow import logic
    logic.release.tag()


@release_cli.command('finish')
def finish():
    # type: () -> None
    """ Merge the current release to both develop and master.

    This will perform a FF merge with develop if possible and --no-ff merge
    with master and then tag the merge commit with the current version.
    """
    from peltak.extra.gitflow import logic
    logic.release.finish()


@release_cli.command('merged')
def merged():
    # type: () -> None
    """ Checkout the target branch, pull and delete the merged branch.

    This is to ease the repetitive cleanup of each merged branch.

    Example Config (those the are defaults)::

        \b
        git:
            devel_branch: 'develop'
            master_branch: 'master'
            protected_branches: ['master', 'develop']

    Example::

        $ peltak release merged     # Must be ran on the relase branch

    """
    from peltak.extra.gitflow import logic
    logic.release.merged()
