# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
Per-project configuration support
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import os.path
import sys
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Dict, Optional, Text, Union

# local imports
from peltak import PKG_DIR
from . import util


PROJ_CONF_FILE = 'pelconf.py'
requirements = []
g_config = {}


def command_requirements(*dependencies):
    # type: (*Text) -> None
    """ Specify python dependencies for the command

    Args:
        *dependencies (str):
            A list of dependencies (pypi package name with version spec) for the
            command. This allows the user to have a list of only

    If you're command requires some python packages to be installed to work
    correctly, call this function once within the module that defines the CLI
    commands and pass all the requirements for your code. This way the user
    can have a list of packages required to install for peltak to work correctly
    and that list will always depend on which commands are included in the
    project configuration.

    Example:

        >>> from peltak.commands import root_cli
        >>> from peltak.core import conf
        >>>
        >>> conf.command_requirements(
        ...     'fancy_dependency~=1.3.0',
        ... )
        >>>
        >>> @root_cli.command('my-command')
        ... def my_command():
        ...     pass

    """
    global requirements
    requirements += dependencies


def init(config):
    # type: (Dict[str, Any]) -> None
    """ Initialize configuration with the given values.

    This should be called from within the project fabfile, before any
    other commands are imported.

    This will not update the existing configuration but replace it entirely.

    Args:
        config (dict[str, Any]):
            The dictionary containing the project configuration.
    """
    global g_config

    g_config = config


def load():
    # type: () -> None
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
    # type: (str) -> None
    """ Load a YAML configuration.

    This will not update the configuration but replace it entirely.

    Args:
        conf_file (str):
            Path to the YAML config. This function will not check the file name
            or extension and will just crash if the given file does not exist or
            is not a valid YAML file.
    """
    global g_config

    with open(conf_file) as fp:
        # Initialize config
        g_config = util.yaml_load(fp)

        # Add src_dir to sys.paths if it's set. This is only done with YAML
        # configs, py configs have to do this manually.
        src_dir = get_path('src_dir', None)
        if src_dir is not None:
            sys.path.insert(0, src_dir)

        for cmd in get('commands', []):
            _import(cmd)


def load_py_config(conf_file):
    # type: (str) -> None
    """ Import configuration from a python file.

    This will just import the file into python. Sky is the limit. The file
    has to deal with the configuration all by itself (i.e. call conf.init()).
    You will also need to add your src directory to sys.paths if it's not the
    current working directory. This is done automatically if you use yaml
    config as well.

    Args:
        conf_file (str):
            Path to the py module config. This function will not check the file
            name or extension and will just crash if the given file does not
            exist or is not a valid python file.
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


def load_template(filename):
    # type: (str) -> str
    """ Load template from file.

    The templates are part of the package and must be included as
    ``package_data`` in project ``setup.py``.

    Args:
        filename (str):
            The template path. Relative to `peltak` package directory.

    Returns:
        str: The content of the chosen template.
    """
    template_file = os.path.join(PKG_DIR, 'templates', filename)
    with open(template_file) as fp:
        return fp.read()


def _import(module):
    # type: (str) -> ModuleType
    return __import__(module)   # nocov


def getenv(name, default=None):
    # type: (str, Any) -> Union[str, Any]
    """ Get the value of an ENV variable. """
    return os.environ.get(name, default)   # nocov


def proj_path(*path_parts):
    # type: (str) -> str
    """ Return absolute path to the repo dir (root project directory).

    Args:
        path (str):
            The path relative to the project root (pelconf.yaml).

    Returns:
        str: The given path converted to an absolute path.
    """
    path_parts = path_parts or ['.']

    # If path represented by path_parts is absolute, do not modify it.
    if not os.path.isabs(path_parts[0]):
        proj_path = _find_proj_root()

        if proj_path is not None:
            path_parts = [proj_path] + list(path_parts)

    return os.path.normpath(os.path.join(*path_parts))


@contextmanager
def within_proj_dir(path='.'):
    # type: (Optional[str]) -> str
    """ Return an absolute path to the given project relative path.

    :param path:
        Project relative path that will be converted to the system wide absolute
        path.
    :return:
        Absolute path.
    """
    curr_dir = os.getcwd()

    os.chdir(proj_path(path))

    yield

    os.chdir(curr_dir)


def get(name, *default):
    # type: (str, Any) -> Any
    """ Get config value with the given name and optional default.

    Args:
        name (str):
            The name of the config value.
        *default (Any):
            If given and the key doesn't not exist, this will be returned
            instead. If it's not given and the config value does not exist,
            AttributeError will be raised

    Returns:
        The requested config value. This is one of the global values defined
        in this file. If the value does not exist it will return `default` if
        give or raise `AttributeError`.

    Raises:
        AttributeError: If the value does not exist and `default` was not given.
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
    # type: (str, Any) -> Any
    """ Get config value as path relative to the project directory.

    This allows easily defining the project configuration within the fabfile
    as always relative to that fabfile.

    Args:
        name (str):
            The name of the config value containing the path.
        *default (Any):
            If given and the key doesn't not exist, this will be returned
            instead. If it's not given and the config value does not exist,
            AttributeError will be raised

    Returns:
        The requested config value. This is one of the global values defined
        in this file. If the value does not exist it will return `default` if
        give or raise `AttributeError`.

    Raises:
        AttributeError: If the value does not exist and `default` was not given.
    """
    global g_config

    value = get(name, *default)

    if value is None:
        return None

    return proj_path(value)


@util.cached_result()
def _find_proj_root():
    # type: () -> Optional[str]
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


# Used in type hint comments only (until we drop python2 support)
del Any, Dict, Optional, Union, Text, ModuleType
