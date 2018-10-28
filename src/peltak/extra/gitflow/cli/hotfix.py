# -*- coding: utf-8 -*-
""" git flow hotfix commands. """
from peltak.cli import root_cli, click


@root_cli.group('hotfix', invoke_without_command=True)
def hotfix_cli():
    # type: () -> None
    """ Commands that ease the work with git flow hotfix branches.

    Examples:

        \b
        $ peltak hotfix start my_hotfix     # Start a new hotfix branch
        $ peltak hotfix finish              # Merge the hotfix into master
        $ peltak hotfix merged              # Cleanup after a remote merge
        $ peltak hotfix rename new_name     # Rename the current hotfix.
    """
    pass


@hotfix_cli.command('start')
@click.argument('name', required=False)
def start(name):
    # type: (str) -> None
    """ Start a new git flow hotfix branch.  """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Hotfix name')

    logic.hotfix.start(name)


@hotfix_cli.command('rename')
@click.argument('name', required=False)
def rename(name):
    # type: (str) -> None
    """ Give the currently developed hotfix a new name. """
    from peltak.extra.gitflow import logic

    if name is None:
        name = click.prompt('Hotfix name')

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
