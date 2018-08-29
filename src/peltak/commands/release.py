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
            'VERSION_FILE': 'src/mypkg/__init__.py'
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
    if not ctx.invoked_subcommand:
        import os
        from peltak.core import shell
        from peltak.core import conf
        from peltak.core import log
        from peltak.core import versioning

        version_file = conf.get_path('VERSION_FILE', 'VERSION')

        with conf.within_proj_dir(quiet=True):
            out = shell.run('git status --porcelain', capture=True).stdout
            lines = out.split(os.linesep)
            has_changes = any(
                not l.startswith('??') for l in lines if l.strip()
            )

        if has_changes:
            log.info("Cannot release: there are uncommitted changes")
            exit(1)

        old_ver, new_ver = versioning.bump(component, exact)

        log.info("Bumping package version")
        log.info("  old version: <35>{}".format(old_ver))
        log.info("  new version: <35>{}".format(new_ver))

        with conf.within_proj_dir(quiet=True):
            branch = 'release/' + new_ver

            log.info("Checking out new branch <35>{}", branch)
            shell.run('git checkout -b ' + branch)

            log.info("Creating commit for the release")

            shell.run('git add {ver_file} && git commit -m "{msg}"'.format(
                ver_file=version_file,
                msg="Releasing v{}".format(new_ver)
            ))


@release_cli.command('tag')
def tag_release():
    """ Tag the current commit with as the current version release.

    This should be the same commit as the one that's uploaded as the release
    (to pypi for example).

    **Example Config**::

        \b
        conf.init({
            'VERSION_FILE': 'src/mypkg/__init__.py'
        })

    Examples::

        $ peltak release tag          # Tag the current commit as release

    """
    from peltak.core import shell
    from peltak.core import conf
    from peltak.core import git
    from peltak.core import log
    from peltak.core import versioning

    release_ver = versioning.current()
    author = git.commit_author()

    with conf.within_proj_dir(quiet=False):
        log.info("Creating tag that marks the release")
        cmd = (
            'git -c "user.name={0.name}" -c "user.email={0.email}" '
            'tag -a "v{1}" -m "Mark v{1} release"'
        ).format(
            author,
            release_ver
        )
        shell.run(cmd)


@release_cli.command()
@click.argument('target')
def upload(target):
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak release uplaod pypi    # Upload the current release to pypi
        $ peltak release uplaod private # Upload to pypi server 'private'

    """
    from peltak.core import shell
    from peltak.core import conf
    from peltak.core import log

    log.info("Uploading to pypi server <33>{}".format(target))
    with conf.within_proj_dir(quiet=False):
        shell.run('python setup.py sdist register -r "{}"'.format(target))
        shell.run('python setup.py sdist upload -r "{}"'.format(target))


@release_cli.command('gen-pypirc')
@click.argument('username', required=False)
@click.argument('password', required=False)
def gen_pypirc(username=None, password=None):
    """
    Generate .pypirc config with the given credentials.

    Example::

        $ peltak release gen-pypirc my_pypi_user my_pypi_pass

    """
    import sys
    from os.path import join
    from peltak.core import conf
    from peltak.core import log

    path = join(conf.getenv('HOME'), '.pypirc')
    username = username or conf.getenv('PYPI_USER', None)
    password = password or conf.getenv('PYPI_PASS', None)

    if username is None or password is None:
        log.err("You must provide $PYPI_USER and $PYPI_PASS")
        sys.exit(1)

    log.info("Generating .pypirc config <94>{}".format(path))

    with open(path, 'w') as fp:
        fp.write('\n'.join((
            '[distutils]',
            'index-servers = ',
            '    pypi',
            '',
            '[pypi]',
            'repository: https://upload.pypi.org/legacy/',
            'username: {}'.format(username),
            'password: {}'.format(password),
            '',
        )))


@release_cli.command('merged')
def merged():
    """ Checkout the target branch, pull and delete the merged branch.

    This is to ease the repetitive cleanup of each merged branch.

    Example Config (those the are defaults)::

        \b
        conf.init({
            'MAIN_BRANCH': 'develop',
            'MASTER_BRANCH': 'master',
            'PROTECTED_BRANCHES': ['master', 'develop'],
            'RELEASE_BRANCH_PATTERN: 'release/*'
        })

    Example::

        $ peltak release merged     # Must be ran on the relase branch

    """
    import sys
    from fnmatch import fnmatch
    from peltak.core import conf
    from peltak.core import git
    from peltak.core import log
    from peltak.core import shell

    develop_branch = conf.get('DEVELOP_BRANCH', 'develop')
    master_branch = conf.get('MASTER_BRANCH', 'master')
    protected_branches = conf.get(
        'PROTECTED_BRANCHES',
        (master_branch, develop_branch)
    )
    release_branch_pattern = conf.get('RELEASE_BRANCH_PATTERN', 'release/*')
    branch = git.current_branch()

    if not fnmatch(branch, release_branch_pattern):
        log.err("You can only merge from release branches. You can specify "
                "The release branch pattern with RELEASE_BRANCH_PATTERN "
                "conf variable (defaults to release/*).")
        sys.exit(1)

    try:
        shell.run('git rev-parse --verify {}'.format(branch))
    except IOError:
        log.err("Branch '{}' does not exist".format(branch))

    # Checkout develop and merge the release
    log.info("Checking out <33>{}".format(develop_branch))
    shell.run('git checkout {}'.format(develop_branch))

    log.info("Merging {} into <33>{}".format(branch, develop_branch))
    shell.run('git merge {}'.format(branch))

    log.info("Checking out <33>{}".format(master_branch))
    shell.run('git checkout {}'.format(master_branch))

    log.info("Pulling latest changes")
    shell.run('git pull origin {}'.format(master_branch))

    if branch not in protected_branches:
        log.info("Deleting branch <33>{}".format(master_branch))
        shell.run('git branch -d {}'.format(master_branch))

    log.info("Pruning")
    shell.run('git fetch --prune origin')

    log.info("Checking out <33>{}<32> branch".format(develop_branch))
    shell.run('git checkout {}'.format(develop_branch))
