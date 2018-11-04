# -*- coding: utf-8 -*-
""" CLI definition. """
from __future__ import absolute_import, unicode_literals

from peltak.commands import root_cli, click


@root_cli.group('changelog', invoke_without_command=True)
@click.pass_context
def changelog_cli(ctx):
    # type: () -> None
    """ Generate changelog from commit messages. """
    if ctx.invoked_subcommand:
        return

    from peltak.core import shell
    from . import logic
    shell.cprint(logic.changelog())
