# -*- coding: utf-8 -*-
""" git flow hotfix commands. """
from peltak.cli import root_cli, click


@root_cli.group('hotfix', invoke_without_command=True)
@click.option(
    '-n', '--name',
    type=str,
    help="The name of the new hotfix."
)
@click.pass_context
def hotfix_cli(ctx, name):
    # type: (click.Context, str) -> None
    """ Start a new git-flow hotfix by branching off master.  """
    if ctx.invoked_subcommand:
        return

    from peltak.extra.gitflow import logic
    logic.hotfix.start(name)


@hotfix_cli.command('rename')
@click.argument('name', type=str)
@click.option(
    '-n', '--name',
    type=str,
    help="The new name for the current hotfix."
)
def rename(name):
    # type: (str) -> None
    """ Give the currently developed hotfix a new name. """
    from peltak.extra.gitflow import logic
    logic.hotfix.rename(name)


@hotfix_cli.command('update')
def update():
    # type: () -> None
    """ Update the hotfix with updates committed to master. """
    from peltak.extra.gitflow import logic
    logic.hotfix.update()


@hotfix_cli.command('finish')
def finish():
    # type: () -> None
    """ Merge current hotfix into master. """
    from peltak.extra.gitflow import logic
    logic.hotfix.finish()


@hotfix_cli.command('merged')
def merged():
    # type: () -> None
    """ Cleanup a remotely merged hotfix. """
    from peltak.extra.gitflow import logic
    logic.hotfix.merged()
