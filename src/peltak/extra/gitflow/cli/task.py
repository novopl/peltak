# -*- coding: utf-8 -*-
""" git flow feature commands. """
from peltak.cli import root_cli, click


@root_cli.group('task', invoke_without_command=True)
def task_cli():
    # type: () -> None
    """ Start a new git-flow task.

    Tasks can only be based on feature branches.
    """
    pass


@task_cli.command('start')
@click.argument('name', required=False)
def start(name):
    # type: (str) -> None
    """ Start a new git-flow feature.  """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Task name')

    logic.task.start(name)


@task_cli.command('rename')
@click.argument('name', required=False)
def rename(name):
    # type: (str) -> None
    """ Give the currently developed feature a new name. """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Task name')

    logic.task.rename(name)


@task_cli.command('update')
def update():
    # type: () -> None
    """ Update the feature with updates committed to develop. """
    from peltak.extra.gitflow import logic
    logic.task.update()


@task_cli.command('finish')
def finish():
    # type: () -> None
    """ Merge current feature into develop. """
    from peltak.extra.gitflow import logic
    logic.task.finish()


@task_cli.command('merged')
def merged():
    # type: () -> None
    """ Cleanup a remotely merged branch. """
    from peltak.extra.gitflow import logic
    logic.task.merged()
