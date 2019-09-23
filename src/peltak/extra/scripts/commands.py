# -*- coding: utf-8 -*-
""" Custom scripts CLI interface. """
from __future__ import absolute_import

from peltak.commands import root_cli, pretend_option
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
    from . import logic

    # This allows defining script options and attaching them to the click
    # command. The drawback is that it does slow auto completion and it might
    # be too slow if we have a lot of scripts. Having one command that just
    # runs the scripts would be probably faster, but won't support custom
    # script options.
    scripts = conf.get('scripts', {})
    for name, script_conf in scripts.items():
        script = logic.Script.from_config(name, script_conf)
        script.register(run_cli)
