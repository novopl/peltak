# -*- coding: utf-8 -*-
""" git flow feature commands. """
from peltak.cli import cli, click


@cli.group('feature', invoke_without_command=True)
@click.option(
    '-n', '--name',
    type=str,
    help="The name of the new feature."
)
@click.pass_context
def feature_cli(ctx, name):
    """ Start a new git-flow feature.  """
    if ctx.invoked_subcommand:
        return

    from peltak.extra.gitflow import impl
    impl.feature.start(name)


@feature_cli.command('rename')
@click.option(
    '-n', '--name',
    type=str,
    help="The new name for the current feature."
)
def rename(name):
    """ Give the currently developed feature a new name. """
    from peltak.extra.gitflow import impl
    impl.feature.rename(name)


@feature_cli.command('update')
def update():
    """ Update the feature with updates committed to develop. """
    from peltak.extra.gitflow import impl
    impl.feature.update()


@feature_cli.command('finish')
def finish():
    """ Merge current feature into develop. """
    from peltak.extra.gitflow import impl
    impl.feature.finish()


@feature_cli.command('merged')
def merged():
    """ Cleanup a remotely merged branch. """
    from peltak.extra.gitflow import impl
    impl.feature.merged()
