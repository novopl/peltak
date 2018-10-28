# -*- coding: utf-8 -*-
""" Code linting commands. """
from __future__ import absolute_import

from typing import List

# local imports
from . import root_cli, click


@root_cli.group('lint', invoke_without_command=True)
@click.option(
    '-e', '--exclude',
    multiple=True,
    metavar='PATTERN',
    help=("Specify patterns to exclude from linting. For multiple patterns, "
          "use the --exclude option multiple times")
)
@click.option(
    '--skip-untracked',
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
@click.pass_context
def lint_cli(ctx, exclude, skip_untracked, commit_only, pretend):
    # type: (click.Context, List[str], bool, bool, bool) -> None
    """ Run pep8 and pylint on all project files.

    You can configure the linting paths using the lint.paths config variable.
    This should be a list of paths that will be linted. If a path to a directory
    is given, all files in that directory and it's subdirectories will be
    used.

    The pep8 and pylint config paths are by default stored in ops/tools/pep8.ini
    and ops/tools/pylint.ini. You can customise those paths in your config with
    lint.pep8_cfg and lint.pylint_cfg variables.

    **Config Example**::

        \b
        lint:
          pylint_cfg: 'ops/tools/pylint.ini'
          pep8_cfg: 'ops/tools/pep8.ini'
          paths:
            - 'src/mypkg'

    **Examples**::

        \b
        $ peltak lint               # Run linter in default mode, skip untracked
        $ peltak lint --commit      # Lint only files staged for commit
        $ peltak lint --all         # Lint all files, including untracked.
        $ peltak lint --pretend     # Print the list of files to lint
        $ peltak lint -e "*.tox*"   # Don't lint files inside .tox directory

    """
    if ctx.invoked_subcommand:
        return

    from peltak.commands import lint
    lint.lint(exclude, skip_untracked, commit_only, pretend)


# Used in docstrings only until we drop python2 support
del List
