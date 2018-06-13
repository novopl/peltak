# -*- coding: utf-8 -*-
"""
Per-project configuration support
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from os import environ, getcwd, listdir
from os.path import abspath, dirname, isabs, join, normpath

# local imports
from . import log


g_config = {}
g_proj_path = None
g_proj_root = None


def is_true(value):
    """ Convert various string values to boolean. """
    try:
        return value.lower() in ('yes', 'y', 'true', 'on')
    except Exception:
        raise ValueError("str_value should be a string.")


def getenv(name, default=None):
    """ Get the value of an ENV variable. """
    return environ.get(name, default)


def proj_path(path=None):
    """ Return absolute path to the repo dir (root project directory). """
    global g_proj_path

    path = path or '.'

    if not isabs(path):
        if g_proj_path is None:
            g_proj_path = _find_proj_root()

        path = normpath(join(g_proj_path, path))

    return path


def _find_proj_root():
    """ Find appengine_sdk in the current $PATH. """
    global g_proj_root

    if g_proj_root is None:
        start_paths = [
            abspath(dirname(__file__)),
            getcwd()
        ]

        log.info('Finding project root')
        for curr in start_paths:
            while curr.startswith('/') and len(curr) > 1:
                log.info('  checking ^94{}', curr)
                if 'fabfile.py' in listdir(curr):
                    log.info('  ^32Found')
                    g_proj_root = curr
                    break
                else:
                    curr = normpath(join(curr, '..'))

            if g_proj_root is not None:
                break

        if g_proj_root is None:
            log.info('  ^31Not found')

    return g_proj_root


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


def init(config):
    """ Initialize configuration with the given values.

    This should be called from within the project fabfile, before any
    other commands are imported

    :param dict config:
        The dictionary containing the project configuration.
    """
    global g_config

    g_config.update(config)
