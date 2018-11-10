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
Functionality related to versioning. This makes project version management
much easier.
"""
from __future__ import absolute_import

# stdlib imports
import json
import re
from collections import OrderedDict
from os.path import exists
from typing import Optional, Tuple

from . import conf
from . import fs


RE_PY_VERSION = re.compile(
    r'__version__\s*=\s*["\']'
    r'(?P<version>\d+(\.\d+(\.\d+)?)?)'
    r'["\']'
)


# MAJOR.MINOR[.PATCH[-BUILD]]
RE_VERSION = re.compile(
    r'^'
    r'(?P<major>\d+)'
    r'(\.(?P<minor>\d+)'
    r'(\.(?P<patch>\d+))?)?'
    r'$'
)


def is_valid(version_str):
    # type: (str) -> bool
    """ Check if the given string is a version string

    Args:
        version_str (str):
            A string to check

    Returns:
        bool: **True** if the given string is a version.
    """
    return bool(version_str and RE_VERSION.match(version_str))


def current():
    # type: () -> str
    """ Return the project's current version.

    Returns:
        str: The current project version in MAJOR.MINOR.PATCH format. PATCH
        might be omitted if it's 0, so 1.0.0 becomes 1.0 and 0.1.0 becomes 0.1.
    """
    storage = get_version_storage()
    return storage.read()


def write(version):
    # type: (str) -> None
    """ Write the given version to the VERSION_FILE """
    if not is_valid(version):
        raise ValueError("Invalid version: ".format(version))

    storage = get_version_storage()
    storage.write(version)


def bump(component='patch', exact=None):
    # type: (str, str) -> Tuple[str, str]
    """ Bump the given version component.

    Args:
        component (str):
            What part of the version should be bumped. Can be one of:

            - major
            - minor
            - patch

        exact (str):
            The exact version that should be set instead of bumping the current
            one.

    Returns:
        tuple(str, str): A tuple of old and bumped version.
    """
    old_ver = current()

    if exact is None:
        new_ver = _bump_version(old_ver, component)
    else:
        new_ver = exact

    write(new_ver)
    return old_ver, new_ver


def _bump_version(version, component='patch'):
    # type: (str, str) -> str
    """ Bump the given version component.

    Args:
        version (str):
            The current version. The format is: MAJOR.MINOR[.PATCH].
        component (str):
            What part of the version should be bumped. Can be one of:

            - major
            - minor
            - patch

    Returns:
        str: Bumped version as a string.
    """
    if component not in ('major', 'minor', 'patch'):
        raise ValueError("Invalid version component: {}".format(component))

    m = RE_VERSION.match(version)
    if m is None:
        raise ValueError("Version must be in MAJOR.MINOR[.PATCH] format")

    major = m.group('major')
    minor = m.group('minor') or '0'
    patch = m.group('patch') or None

    if patch == '0':
        patch = None

    if component == 'major':
        major = str(int(major) + 1)
        minor = '0'
        patch = None

    elif component == 'minor':
        minor = str(int(minor) + 1)
        patch = None

    else:
        patch = patch or 0
        patch = str(int(patch) + 1)

    new_ver = '{}.{}'.format(major, minor)
    if patch is not None:
        new_ver += '.' + patch

    return new_ver


class VersionStorage(object):
    """ Base class for version storage.

    A version storage is a way to store the project version. Different projects
    will have different ways of storing the version. The simplest case is a
    text file that holds just the version number (probably called VERSION).
    Python projects can also use a version stored as ``__version__`` variable
    inside the project package/module. A Node.js project on the other hand will
    probably keep the version in ``package.json``. All of the above strategies
    can be (and are) implemented through subclassing this class.

    @see `PyVersionStorage`, `RawVersionStorage`, `NodeVersionStorage`
    """
    def __init__(self, version_file):
        # type: (str) -> None
        self.version_file = version_file

        if not exists(version_file):
            raise ValueError("Version file '{}' does not exist.".format(
                version_file
            ))

    def read(self):
        # type: () -> Optional[str]
        """ Read the current project version.

        All subclasses must implement this method.

        Raises:
            NotImplementedError:
                If the subclass does nto implement the read() method.
        """
        raise NotImplementedError("{} must implement .read()".format(
            self.__class__.__name__
        ))

    def write(self, version):
        # type: (str) -> None
        """ Save the given version as the current project version.

        All subclasses must implement this method.

        Raises:
            NotImplementedError:
                If the subclass does nto implement the write() method.
        """
        raise NotImplementedError("{} must implement .write()".format(
            self.__class__.__name__
        ))


class PyVersionStorage(VersionStorage):
    """ Store project version in one of the py module/package files. """
    def read(self):
        # type: () -> Optional[str]
        """ Read the project version from .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and read the version string.
        """
        with open(self.version_file) as fp:
            content = fp.read()
            m = RE_PY_VERSION.search(content)
            if not m:
                return None
            else:
                return m.group('version')

    def write(self, version):
        # type: (str) -> None
        """ Write the project version to .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and substitute the version string
        for the new version.
        """
        with open(self.version_file) as fp:
            content = fp.read()

        ver_statement = "__version__ = '{}'".format(version)
        new_content = RE_PY_VERSION.sub(ver_statement, content)
        fs.write_file(self.version_file, new_content)


class RawVersionStorage(VersionStorage):
    """ Store project version as a simple value in a text file. """
    def read(self):
        # type: () -> Optional[str]
        """ Read the project version from .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and read the version string.
        """
        with open(self.version_file) as fp:
            version = fp.read().strip()

            if is_valid(version):
                return version

            return None

    def write(self, version):
        # type: (str) -> None
        fs.write_file(self.version_file, version)


class NodeVersionStorage(VersionStorage):
    """ Store project version in package.json. """
    def read(self):
        # type: () -> Optional[str]
        with open(self.version_file) as fp:
            config = json.load(fp)
            return config.get('version')

    def write(self, version):
        # type: (str) -> None
        with open(self.version_file, 'r') as fp:
            config = json.load(fp, object_pairs_hook=OrderedDict)

        config['version'] = version

        fs.write_file(self.version_file, json.dumps(config, indent=2))


def get_version_storage():
    # type: () -> VersionStorage
    """ Get version storage for the given version file.

    The storage engine used depends on the extension of the *version_file*.
    """
    version_file = conf.get_path('version_file', 'VERSION')
    if version_file.endswith('.py'):
        return PyVersionStorage(version_file)
    elif version_file.endswith('package.json'):
        return NodeVersionStorage(version_file)
    else:
        return RawVersionStorage(version_file)


# Used in docstrings only until we drop python2 support
del Optional, Tuple
