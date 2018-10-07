# -*- coding: utf-8 -*-
""" git flow hotfix commands. """
from peltak.cli import cli, click


@cli.group('hotfix', invoke_without_command=True)
@click.option(
    '-n', '--name',
    type=str,
    help="The name of the new hotfix."
)
@click.pass_context
def hotfix_cli(ctx, name):
    """ Start a new git-flow hotfix by branching off master.  """
    if ctx.invoked_subcommand:
        return

    from peltak.extra.gitflow import impl
    impl.hotfix.start(name)


@hotfix_cli.command('rename')
@click.argument('name', type=str)
@click.option(
    '-n', '--name',
    type=str,
    help="The new name for the current hotfix."
)
def rename(name):
    """ Give the currently developed hotfix a new name. """
    from peltak.extra.gitflow import impl
    impl.hotfix.rename(name)


@hotfix_cli.command('update')
def update():
    """ Update the hotfix with updates committed to master. """
    from peltak.extra.gitflow import impl
    impl.hotfix.update()


@hotfix_cli.command('finish')
def finish():
    """ Merge current hotfix into master. """
    from peltak.extra.gitflow import impl
    impl.hotfix.finish()


@hotfix_cli.command('merged')
def merged():
    """ Cleanup a remotely merged hotfix. """
    from peltak.extra.gitflow import impl
    impl.hotfix.merged()
