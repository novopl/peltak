# -*- coding: utf-8 -*-
""" Frontend commands implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os.path import exists, join

# local imports
from peltak.core import conf
from peltak.core import log
from peltak.core import shell


def fe(cmd):
    """ Run a frontend command.

    The commands are defined in the project config.

    :param str cmd:
        Frontend command to run.
    """
    frontend_cmds = conf.get('frontend.commands', {
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
        log.err("No {} in frontend.commands".format(cmd))


def init_fe(skip_if_exists):
    """ Initialize frontend.

    This is a little shortcut for ``npm init``. The main difference is that
    by default it will not do anything if ``node_modules`` directory is already
    present. Useful for CI runs when you have your node_modules cached and you
    know nothing changed but you still want to run it if the ``node_modules``
    directory is m

    :param skip_if_exists:
    :return:
    """
    frontend_path = conf.get_path('frontend.path', None)
    initialized = exists(join(frontend_path, 'node_modules'))

    if not initialized or not skip_if_exists:
        _fe_cmd('npm install')


def _fe_cmd(cmd):
    frontend_path = conf.get_path('frontend.path', None)

    if frontend_path is not None:
        with conf.within_proj_dir(frontend_path):
            shell.run(cmd)
    else:
        log.err("No frontend.path defined in the config")
