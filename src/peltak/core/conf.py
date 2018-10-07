# -*- coding: utf-8 -*-
"""
Per-project configuration support
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import os.path
import sys
from contextlib import contextmanager

# 3rd party imports
import yaml

# local imports
from . import util


PROJ_CONF_FILE = 'pelconf.py'
g_config = {}


def init(config):
    """ Initialize configuration with the given values.

    This should be called from within the project fabfile, before any
    other commands are imported.

    This will not update the existing configuration but replace it entirely.

    :param dict config:
        The dictionary containing the project configuration.
    """
    global g_config

    g_config = config


def load():
    """ Load configuration from file.

    This will search the directory structure upwards to find the project root
    (directory containing ``pelconf.py`` file). Once found it will import the
    config file which should initialize all the configuration (using
    `peltak.core.conf.init()` function).

    You can also have both yaml (configuration) and python (custom commands)
    living together. Just remember that calling `conf.init()` will overwrite
    the config defined in YAML.
    """
    with within_proj_dir():
        if os.path.exists('pelconf.yaml'):
            load_yaml_config('pelconf.yaml')

        if os.path.exists('pelconf.py'):
            load_py_config('pelconf.py')


def load_yaml_config(conf_file):
    """ Load a YAML configuration.

    This will not update the configuration but replace it entirely.

    :param str conf_file:
        Path to the YAML config. This function will not check the file name
        or extension and will just crash if the given file does not exist or
        is not a valid YAML file.
    """
    global g_config

    with open(conf_file) as fp:
        # Initialize config
        g_config = yaml.load(fp)

        # Add src_dir to sys.paths if it's set. This is only done with YAML
        # configs, py configs have to do this manually.
        src_dir = get_path('src_dir', None)
        if src_dir is not None:
            sys.path.insert(0, src_dir)

        for cmd in get('commands', []):
            _import(cmd)


def load_py_config(conf_file):
    """ Import configuration from a python file.

    This will just import the file into python. Sky is the limit. The file
    has to deal with the configuration all by itself (i.e. call conf.init()).
    You will also need to add your src directory to sys.paths if it's not the
    current working directory. This is done automatically if you use yaml
    config as well.

    :param str conf_file:
        Path to the YAML config. This function will not check the file name
        or extension and will just crash if the given file does not exist or
        is not a valid python file.
    """
    if sys.version_info >= (3, 5):
        from importlib import util

        spec = util.spec_from_file_location('pelconf', conf_file)
        mod = util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    elif sys.version_info >= (3, 3):
        from importlib import machinery
        loader = machinery.SourceFileLoader('pelconf', conf_file)
        _ = loader.load_module()

    elif sys.version_info <= (3, 0):
        import imp

        imp.load_source('pelconf', conf_file)


def _import(module):
    return __import__(module)   # nocov


def getenv(name, default=None):
    """ Get the value of an ENV variable. """
    return os.environ.get(name, default)   # nocov


def proj_path(path=None):
    """ Return absolute path to the repo dir (root project directory). """
    path = path or '.'

    if not os.path.isabs(path):
        proj_path = _find_proj_root()

        if proj_path is not None:
            path = os.path.normpath(os.path.join(proj_path, path))

    return path


@contextmanager
def within_proj_dir(path='.'):
    """ Return an absolute path to the given project relative path.

    :param str path:
        Project relative path that will be converted to the system wide absolute
        path.
    :return str:
        Absolute path.
    """
    curr_dir = os.getcwd()

    os.chdir(proj_path(path))

    yield

    os.chdir(curr_dir)


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

    curr = g_config
    for part in name.split('.'):
        if part in curr:
            curr = curr[part]
        elif default:
            return default[0]
        else:
            raise AttributeError("Config value '{}' does not exist".format(
                name
            ))

    return curr


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

    value = get(name, *default)

    if value is None:
        return None

    return proj_path(value)


@util.cached_result()
def _find_proj_root():
    """ Find the project path by going up the file tree.

    This will look in the current directory and upwards for the pelconf file
    (.yaml or .py)
    """
    proj_files = frozenset(('pelconf.py', 'pelconf.yaml'))
    curr = os.getcwd()

    while curr.startswith('/') and len(curr) > 1:
        if proj_files & frozenset(os.listdir(curr)):
            return curr
        else:
            curr = os.path.dirname(curr)

    return None
