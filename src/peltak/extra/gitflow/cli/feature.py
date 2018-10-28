# -*- coding: utf-8 -*-
""" git flow feature commands. """
from peltak.cli import root_cli, click


@root_cli.group('feature', invoke_without_command=True)
def feature_cli():
    # type: () -> None
    """ Start a new git-flow feature.  """


@feature_cli.command('start')
@click.argument('name', required=False)
def start(name):
    # type: (str) -> None
    """ Start a new git-flow feature.  """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Feature name')

    logic.feature.start(name)


@feature_cli.command('rename')
@click.argument('name', required=False)
def rename(name):
    # type: (str) -> None
    """ Give the currently developed feature a new name. """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Feature name')

    logic.feature.rename(name)


@feature_cli.command('update')
def update():
    # type: () -> None
    """ Update the feature with updates committed to develop. """
    from peltak.extra.gitflow import logic
    logic.feature.update()


@feature_cli.command('finish')
def finish():
    # type: () -> None
    """ Merge current feature into develop. """
    from peltak.extra.gitflow import logic
    logic.feature.finish()


@feature_cli.command('merged')
def merged():
    # type: () -> None
    """ Cleanup a remotely merged branch. """
    from peltak.extra.gitflow import logic
    logic.feature.merged()
