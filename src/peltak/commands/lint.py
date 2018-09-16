# -*- coding: utf-8 -*-
""" Code linting commands. """
from __future__ import absolute_import
from . import cli, click


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
    from .impl import lint

    lint.lint(exclude, include_untracked, commit_only, pretend)
