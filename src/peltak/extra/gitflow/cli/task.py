# -*- coding: utf-8 -*-
""" git flow feature commands. """
from peltak.cli import cli, click


@cli.group('task', invoke_without_command=True)
@click.option(
    '-n', '--name',
    type=str,
    help="The name of the new task."
)
@click.pass_context
def task_cli(ctx, name):
    """ Start a new git-flow task.

    Tasks can only be based on feature branches.
    """
    if ctx.invoked_subcommand:
        return

    if name is None:
        name = click.prompt('Name of the new task')

    from peltak.extra.gitflow import impl
    impl.task.start(name)


@task_cli.command('rename')
@click.option(
    '-n', '--name',
    type=str,
    help="The new name for the current feature."
)
def rename(name):
    """ Give the currently developed feature a new name. """
    from peltak.extra.gitflow import impl
    impl.task.rename(name)


@task_cli.command('update')
def update():
    """ Update the feature with updates committed to develop. """
    from peltak.extra.gitflow import impl
    impl.task.update()


@task_cli.command('finish')
def finish():
    """ Merge current feature into develop. """
    from peltak.extra.gitflow import impl
    impl.task.finish()


@task_cli.command('merged')
def merged():
    """ Cleanup a remotely merged branch. """
    from peltak.extra.gitflow import impl
    impl.task.merged()
