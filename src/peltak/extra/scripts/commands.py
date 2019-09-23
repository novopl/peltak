# -*- coding: utf-8 -*-
""" Custom scripts CLI interface. """
from __future__ import absolute_import

from peltak.commands import click, root_cli, pretend_option
from peltak.core import hooks


@root_cli.group('run')
@pretend_option
def run_cli():
    # type: () -> None
    """ Run custom scripts """
    pass


@hooks.register('post-conf-load')
def post_conf_load():
    """ After the config was loaded, register all scripts as click commands. """
    from peltak.core import conf

    # This allows defining script options and attaching them to the click
    # command. The drawback is that it does slow auto completion and it might
    # be too slow if we have a lot of scripts. Having one command that just
    # runs the scripts would be probably faster, but won't support custom
    # script options.

    # log.info("Config loaded:")
    scripts = conf.get('scripts', {})

    for name, script in scripts.items():
        _make_script_command(name, script)


def _make_script_command(name, script):
    @click.pass_context
    def script_command(ctx):    # pylint: disable=missing-docstring
        _exec_script(name, script, ctx)

    script_command.__doc__ = script['about']

    return run_cli.command(name)(script_command)


def _exec_script(name, script, ctx):
    from peltak.core import log
    from peltak.core import shell

    command = script['command']

    log.info("Executing script: {}", name, ctx)
    log.info('<90>\n{}', command)
    shell.run(command)
