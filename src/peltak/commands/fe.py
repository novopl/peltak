# -*- coding: utf-8 -*-
""" Frontend related commands.

All frontend commands should be implemented through
``src/frontend/package.json``. This is just a proxy to allow easily running
them from the root project directory.
"""
from __future__ import absolute_import
from . import cli, click


@cli.command('fe')
@click.argument('cmd')
def fe(cmd):
    """ Run a predefined frontend command.

    The commands can be defined through the frontend.commands project
    configuration value. It should be a dict of commands mapped to the actual
    scripts ran inside the frontend.path.

    This command is mostly helpful if frontend code base is a subdirectory of
    the project. This is a very thin wrapper around javascript task runners,
    but it allows to run those commands from within any subdirectory of the
    project (as the root is defined by ``pelconf.py`` and not ``package.json``.

    If you only run frontend commands from within the frontend directory then
    this command is probably an unnecessary overhead.

    Sample Config::

        \b
        conf.init({
            'frontend': {
                'path': 'client/webui',
                'commands': {
                    'build': 'npm run build',
                    'watch': 'npm run watch'
                }
            }
        })

    Examples::

        \b
        $ peltak fe build       # Run frontend command named 'build'
        $ peltak fe watch       # Run frontend command named 'watch'
    """
    from .impl import fe

    fe.fe(cmd)


@cli.command('init-fe')
@click.argument('cmd')
@click.option(
    '--no-recreate', 'skip_if_exists',
    is_flag=True,
    help="Do nothing if node_modules already exists"
)
def init_fe(skip_if_exists):
    """ Initialize frontend.

    This is a little shortcut for ``npm init``. The main difference is that
    by default it will not do anything if ``node_modules`` directory is already
    present. Useful for CI runs when you have your node_modules cached and you
    know nothing changed but you still want to run it if the ``node_modules``
    directory is missing.

    Config Sample::

        \b
        conf.init({
            'frontend': {
                'path': 'client/webui'
            }
        })

    Examples::

        \b
        $ peltak init-fe                # Run 'npm-init'
        $ peltak init-fe --no-recreate  # Run only if node_modules is missing

    """
    from .impl import fe

    fe.init_fe(skip_if_exists)
