# -*- coding: utf-8 -*-
""" Frontend related commands.

All frontend commands should be implemented through
``src/frontend/package.json``. This is just a proxy to allow easily running
them from the root project directory.
"""
from __future__ import absolute_import
from . import cli, click


def _fe_cmd(cmd):
    from peltak.core import conf
    from peltak.core import log
    from peltak.core import shell

    frontend_path = conf.get_path('FRONTEND_PATH', None)

    if frontend_path is not None:
        with conf.within_proj_dir(frontend_path):
            shell.run(cmd)
    else:
        log.err("No FRONTEND_PATH defined in the config")


@cli.command('fe')
@click.argument('cmd')
def fe(cmd):
    """ Run a predefined frontend command.

    The commands can be defined through the FRONTEND_CMDS project configuration
    value. It should be a dict of commands mapped to the actual scripts ran
    inside the FRONTEND_DIR.

    This command is mostly helpful if frontend code base is a subdirectory of
    the project. This is a very thin wrapper around javascript task runners,
    but it allows to run those commands from within any subdirectory of the
    project (as the root is defined by ``pelconf.py`` and not ``package.json``.

    If you only run frontend commands from within the frontend directory then
    this command is probably an unnecessary overhead.

    Sample Config::

        \b
        conf.init({
            'FRONTEND_DIR': 'client/webui',
            'FRONTEND_CMDS': {
                'build': 'npm run build',
                'watch': 'npm run watch'
            }
        })

    Examples::

        \b
        $ peltak fe build       # Run frontend command named 'build'
        $ peltak fe watch       # Run frontend command named 'watch'
    """
    from peltak.core import conf
    from peltak.core import log

    frontend_cmds = conf.get('FRONTEND_CMDS', {
        'build': 'npm run build',
        'start': 'npm start',
        'watch': 'npm run watch',
        'test': 'npm test',
        'lint': 'npm lint',
        'check': 'npm run lint && npm run test'
    })

    if cmd in frontend_cmds:
        _fe_cmd(frontend_cmds[cmd])
    else:
        log.err("No {} in FRONTEND_CMDS".format(cmd))


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
            'FRONTEND_PATH': 'client/webui'
        })

    Examples::

        \b
        $ peltak init-fe                # Run 'npm-init'
        $ peltak init-fe --no-recreate  # Run only if node_modules is missing

    """
    from os.path import exists, join
    from peltak.core import conf

    frontend_path = conf.get_path('FRONTEND_PATH', None)
    initialized = exists(join(frontend_path, 'node_modules'))

    if not initialized or not skip_if_exists:
        _fe_cmd('npm install')
