# -*- coding: utf-8 -*-
"""
Per-project configuration support
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import subprocess
import sys
from collections import namedtuple
from contextlib import contextmanager
from os.path import abspath, dirname, isabs, join, normpath

# local imports
from . import log


g_config = {}
g_proj_path = None
g_proj_root = None
PROJ_CONF_FILE = 'pelconf.py'


ExecResult = namedtuple(
    'ExecResult',
    'command return_code stdout stderr succeeded failed'
)


def init(config):
    """ Initialize configuration with the given values.

    This should be called from within the project fabfile, before any
    other commands are imported

    :param dict config:
        The dictionary containing the project configuration.
    """
    global g_config

    g_config.update(config)


def load():
    if proj_path() is None:
        return

    with within_proj_dir():
        if sys.version_info >= (3, 5):
            from importlib.util import spec_from_file_location
            from importlib.util import module_from_spec

            spec = spec_from_file_location('pelconf', 'pelconf.py')
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)

        elif sys.version_info >= (3, 3):
            from importlib.machinery import SourceFileLoader
            loader = SourceFileLoader('pelconf', 'pelconf.py')
            mod = loader.load_module()

        elif sys.version_info <= (3, 0):
            import imp

            imp.load_source('pelconf', 'pelconf.py')


def getenv(name, default=None):
    """ Get the value of an ENV variable. """
    return os.environ.get(name, default)


def proj_path(path=None):
    """ Return absolute path to the repo dir (root project directory). """
    global g_proj_path

    path = path or '.'

    if not isabs(path):
        if g_proj_path is None:
            g_proj_path = _find_proj_root()

        if g_proj_path is not None:
            path = normpath(join(g_proj_path, path))

    return path


@contextmanager
def within_proj_dir(path='.', quiet=False):
    """ Return absolute path to the repo dir (root project directory). """
    curr_dir = os.getcwd()

    os.chdir(proj_path(path))

    yield

    os.chdir(curr_dir)


def run(cmd, capture=False, shell=True, env=None):
    options = {
        'bufsize': 1,       # line buffered
        'shell': shell
    }

    if capture:
        options.update({
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
        })

    if env is not None:
        options['env'] = dict(os.environ)
        options['env'].update(env)

    p = subprocess.Popen(cmd, **options)
    stdout, stderr = p.communicate()

    try:
        if stdout is not None:
            stdout = stdout.decode('utf-8')

        if stderr is not None:
            stderr = stderr.decode('utf-8')
    except AttributeError:
        # 'str' has no attribute 'decode'
        pass

    if capture is False and p.returncode != 0:
        sys.exit(p.returncode)

    return ExecResult(
        cmd,
        p.returncode,
        stdout,
        stderr,
        p.returncode == 0,
        p.returncode != 0
    )


def get(name, *default):
    """ Get config value with the given name and optional default.

    :param str|unicode name:
        The name of the config value.
    :param Any default:
        If given and the key doesn't not exist, this will be returned instead.
        If it's not given and the config value does not exist, AttributeError
        will be raised
    :return Any:
        The requested config value. This is one of the global values defined
        in this file.
    """
    global g_config

    if name in g_config:
        return g_config[name]
    elif default:
        return default[0]
    else:
        raise AttributeError("Config value '{}' does not exist".format(name))


def get_path(name, *default):
    """ Get config value as path relative to the project directory.

    This allows easily defining the project configuration within the fabfile
    as always relative to that fabfile.

    :param str|unicode name:
        The name of the config value containing the path.
    :param Any default:
        If given and the key doesn't not exist, this will be returned instead.
        If it's not given and the config value does not exist, AttributeError
        will be raised
    :return Any:
        The requested config value. This is one of the global values defined
        in this file.
    """
    global g_config

    if name in g_config:
        return proj_path(g_config[name])
    elif default:
        if default[0] is None:
            return None
        else:
            return proj_path(default[0])
    else:
        raise AttributeError("Config value '{}' does not exist".format(name))


def _find_proj_root():
    """ Find appengine_sdk in the current $PATH. """
    global g_proj_root

    if g_proj_root is None:
        start_paths = [
            abspath(dirname(__file__)),
            os.getcwd()
        ]

        # log.info('Finding project root')
        for curr in start_paths:
            while curr.startswith('/') and len(curr) > 1:
                # log.info('  checking ^94{}', curr)
                if PROJ_CONF_FILE in os.listdir(curr):
                    # log.info('  ^32Found')
                    g_proj_root = curr
                    break
                else:
                    curr = normpath(join(curr, '..'))

            if g_proj_root is not None:
                break

        if g_proj_root is None:
            # log.info('  ^31Not found')
            pass

    return g_proj_root
