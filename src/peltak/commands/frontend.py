# -*- coding: utf-8 -*-
""" Frontend related commands.

All frontend commands should be implemented through
``src/frontend/package.json``. This is just a proxy to allow easily running
them from the root project directory.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import exists, join

# 3rd party imports
import click

# local imports
from peltak.core import conf
from peltak.core import log
from peltak.core import shell
from . import cli


FRONTEND_PATH = conf.get_path('FRONTEND_PATH', None)
FRONTEND_CMDS = conf.get('FRONTEND_CMDS', {
    'build': 'npm run build',
    'start': 'npm start',
    'watch': 'npm run watch',
    'test': 'npm test',
    'lint': 'npm lint',
    'check': 'npm run lint && npm run test'
})


def _fe_cmd(cmd):
    if FRONTEND_PATH is not None:
        with conf.within_proj_dir(FRONTEND_PATH):
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
    if cmd in FRONTEND_CMDS:
        _fe_cmd(FRONTEND_CMDS[cmd])
    else:
        log.err("No {} in FRONTEND_CMDS".format(cmd))


@cli.command('init-fe')
@click.argument('cmd')
@click.option('--no-recreate', is_flag=True)
def init_fe(no_recreate=False):
    """ Initialize frontend. """
    initialized = exists(join(FRONTEND_PATH, 'node_modules'))

    if not (initialized and no_recreate):
        _fe_cmd('npm install')
