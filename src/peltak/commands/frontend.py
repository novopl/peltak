# -*- coding: utf-8 -*-
""" Frontend related commands.

All frontend commands should be implemented through
``src/frontend/package.json``. This is just a proxy to allow easily running
them from the root project directory.
"""
from __future__ import absolute_import, unicode_literals
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


@cli.command()
@click.argument('cmd')
def fe(cmd):
    """ Run a predefined frontend command.

    The commands can be defined through the FRONTEND_CMDS project configuration
    value. It should be a dict of commands mapped to the actual scripts ran
    inside the FRONTEND_DIR.
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
@click.option('--no-recreate', is_flag=True)
def init_fe(no_recreate=False):
    """ Initialize frontend. """
    from os.path import exists, join
    from peltak.core import conf

    frontend_path = conf.get_path('FRONTEND_PATH', None)
    initialized = exists(join(frontend_path, 'node_modules'))

    if not (initialized and no_recreate):
        _fe_cmd('npm install')
