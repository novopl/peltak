# -*- coding: utf-8 -*-
""" Custom command definitions for the project. """
from __future__ import absolute_import, unicode_literals

from peltak.commands import root_cli, click


@root_cli.command('hello-world')
def hello_world():
    """ Hello world command. """
    print('Hello, World!')


@root_cli.command('lint')
@click.argument(
    'paths',
    nargs=-1,
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    '-i', '--include',
    multiple=True,
    help='A pattern to include in linting. Can be passed multiple times. This '
         'can be used to limit the results in the given paths to only files '
         'that match the include patterns.',
)
@click.option(
    '-e', '--exclude',
    multiple=True,
    help='A pattern to exclude from linting. Can be passed multiple times.',
)
@click.option(
    '--commit', 'only_staged',
    is_flag=True,
    help='If given, only files staged for commit will be checked.',
)
@click.option(
    '--ignore-untracked',
    is_flag=True,
    help='Include untracked files',
)
def lint(paths, include, exclude, only_staged, ignore_untracked):
    """ Run code checks (pylint + mypy) """
    from peltak.core import log
    from custom_commands_logic import check

    log.info('<0><1>{}', '-' * 60)
    log.info('paths:            {}', paths)
    log.info('include:          {}', include)
    log.info('exclude:          {}', exclude)
    log.info('only_staged:      {}', only_staged)
    log.info('ignore_untracked: {}', ignore_untracked)
    log.info('<0><1>{}', '-' * 60)

    check(
        paths=paths,
        include=include,
        exclude=exclude,
        only_staged=only_staged,
        untracked=not ignore_untracked,
    )
