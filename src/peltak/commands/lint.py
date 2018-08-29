# -*- coding: utf-8 -*-
""" Code linting commands. """
from __future__ import absolute_import
from . import cli, click


def _lint_files(paths, include=None, exclude=None, pretend=False):
    """ Run static analysis on the given files.

    :param paths:   Iterable with each item being path that should be linted..
    """
    from itertools import chain
    from six import string_types
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import log
    from peltak.core import shell
    from peltak.core import util

    pylint_cfg_path = conf.get_path('PYLINT_CFG_PATH', 'ops/tools/pylint.ini')
    pep8_cfg_path = conf.get_path('PEP8_CFG_PATH', 'ops/tools/pep8.ini')

    if isinstance(paths, string_types):
        raise ValueError("paths must be an array of strings")

    with util.timed_block() as t:
        files = list(chain.from_iterable(
            fs.filtered_walk(p, include, exclude) for p in paths
        ))

    log.info("Paths to lint:")
    for path in paths:
        log.info("  <0>{}", path)

    log.info("Files:")
    for p in files:
        log.info("  <0>{}", p)

    log.info("Collected <33>{} <32>files in <33>{}ms".format(
        len(files), t.elapsed_ms
    ))

    if not pretend:
        log.info("Checking PEP8 compatibility")
        files = fs.surround_paths_with_quotes(files)

        with util.timed_block() as t:
            pep8_cmd = 'pep8 --config {} {}'.format(pep8_cfg_path, files)
            pep8_ret = shell.run(pep8_cmd).return_code

            log.info("Running linter")
            pylint_cmd = 'pylint --rcfile {} {}'.format(pylint_cfg_path, files)
            pylint_ret = shell.run(pylint_cmd).return_code

        log.info("Code checked in <33>{}s", t.elapsed_s)

        if pep8_ret != 0:
            log.info("pep8 failed with return code {}", pep8_ret)

        if pylint_ret:
            log.info("pylint failed with return code {}", pylint_ret)

        return pep8_ret == pylint_ret == 0

    return True


@cli.command('lint')
@click.option(
    '-e', '--exclude',
    multiple=True,
    metavar='PATTERN',
    help=("Specify patterns to exclude from linting. For multiple patterns, "
          "use the --exclude option multiple times")
)
@click.option(
    '--all', 'include_untracked',
    is_flag=True,
    help="Also include files not tracked by git."
)
@click.option(
    '--commit', 'commit_only',
    is_flag=True,
    help=("Only lint files staged for commit. Useful if you want to clean up "
          "a large code base one commit at a time.")
)
@click.option(
    '-p', '--pretend',
    is_flag=True,
    help=("Just print files that would be linted without running anything")
)
def lint(exclude, include_untracked, commit_only, pretend):
    """ Run pep8 and pylint on all project files.

    You can configure the linting paths using the LINT_PATHS config variable.
    This should be a list of paths that will be linted. If a path to a directory
    is given, all files in that directory and it's subdirectories will be
    used.

    The pep8 and pylint config paths are by default stored in ops/tools/pep8.ini
    and ops/tools/pylint.ini. You can customise those paths in your config with
    PEP8_CFG_PATH and PYLINT_CFG_PATH variables.

    **Config Example**::

        \b
        conf.init({
            'PYLINT_CFG_PATH': 'ops/tools/pylint.ini',
            'PEP8_CFG_PATH': 'ops/tools/pep8.ini',
            'LINT_PATHS': [
                'src/mypkg'
            ],
        })

    **Examples**::

        \b
        $ peltak lint               # Run linter in default mode, skip untracked
        $ peltak lint --commit      # Lint only files staged for commit
        $ peltak lint --all         # Lint all files, including untracked.
        $ peltak lint --pretend     # Print the list of files to lint
        $ peltak lint -e "*.tox*"   # Don't lint files inside .tox directory

    """
    from peltak.core import conf
    from peltak.core import git

    paths = [conf.proj_path(p) for p in conf.get('LINT_PATHS', [])]
    include = ['*.py']
    exclude = list(exclude)     # Convert from tuple to easily concatenate.

    if commit_only:
        include += ['*' + f for f in git.staged() if f.endswith('.py')]
        exclude += git.ignore()

    if not include_untracked:
        exclude += git.untracked()

    if not _lint_files(paths, include, exclude, pretend):
        exit(1)
