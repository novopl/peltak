# -*- coding: utf-8 -*-
"""
Functionality related to versioning. This makes project version management
much easier.
"""
from __future__ import absolute_import

# stdlib imports
import json
import os
import re
from collections import OrderedDict
from os.path import exists

from . import conf


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
    """ Check if the given string is a version string

    :param str|unicode version_str:
        A string to check
    :return bool:
        **True** if the given string is a version.
    """
    return bool(version_str and RE_VERSION.match(version_str))


def current():
    """ Return the project's current version.

    :return Union[str,unicode]:
        The current project version in MAJOR.MINOR.PATCH format. PATCH might be
        omitted if it's 0, so 1.0.0 becomes 1.0 and 0.1.0 becomes 0.1.
    """
    storage = get_version_storage()
    return storage.read()


def write(version):
    """ Write the given version to the VERSION_FILE """
    if not is_valid(version):
        raise ValueError("Invalid version: ".format(version))

    storage = get_version_storage()
    storage.write(version)


def bump(component='patch', exact=None):
    """ Bump the given version component.

    :param str component:
        What part of the version should be bumped. Can be one of:

        - major
        - minor
        - patch

    :param Optional[str] exact:
        The exact version that should be set instead of bumping the current one.

    :return str:
        Bumped version as a string.
    """
    old_ver = current()

    if exact is None:
        new_ver = _bump_version(old_ver, component)
    else:
        new_ver = exact

    write(new_ver)
    return old_ver, new_ver


def _bump_version(version, component='patch'):
    """ Bump the given version component.

    :param str version:
        The current version. The format is: MAJOR.MINOR[.PATCH].
    :param str component:
        What part of the version should be bumped. Can be one of:

        - major
        - minor
        - patch

    :return str:
        Bumped version as a string.
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
    """ Base class for version storages.

    A version storage is a way to store the project version. Different projects
    will have different ways of storing the version. The simpliest case is a
    text file that holds just the version number (probably called VERSION).
    Python projects can also use a version stored as ``__version__`` variable
    inside the project package/module. A Node.js project on the other hand will
    probably keep the version in ``package.json``. All of the above strategies
    can be (and are) implemented through sublcassing this class.

    @see `PyVersionStorage`, `RawVersionStorage`, `NodeVersionStorage`
    """
    def __init__(self, version_file):
        self.version_file = version_file

        if not exists(version_file):
            raise ValueError("Version file '{}' does not exist.".format(
                version_file
            ))

    def read(self):
        """ Read the current project version.

        All subclasses must implement this method.
        """
        raise NotImplementedError("{} must implement .read()".format(
            self.__class__.__name__
        ))

    def write(self, version):
        """ Save the given version as the current project version.

        All subclasses must implement this method.
        """
        raise NotImplementedError("{} must implement .write()".format(
            self.__class__.__name__
        ))


class PyVersionStorage(VersionStorage):
    """ Store project version in one of the py module/package files. """
    def read(self):
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
        """ Write the project version to .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and substitute the version string
        for the new version.
        """
        with open(self.version_file) as fp:
            content = fp.read()

        ver_statement = "__version__ = '{}'".format(version)
        new_content = RE_PY_VERSION.sub(ver_statement, content)

        with open(self.version_file, 'w') as fp:
            fp.write(new_content)


class RawVersionStorage(VersionStorage):
    """ Store project version as a simple value in a text file. """
    def read(self):
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
        with open(self.version_file, 'w') as fp:
            fp.write(version)


class NodeVersionStorage(VersionStorage):
    """ Store project version in package.json. """
    def read(self):
        with open(self.version_file) as fp:
            config = json.load(fp)
            return config.get('version')

    def write(self, version):
        with open(self.version_file, 'rw') as fp:
            config = json.load(fp, object_pairs_hook=OrderedDict)

            config['version'] = version
            data = json.dumps(config, indent=2)

            fp.seek(0, os.SEEK_SET)
            fp.write(data)


def get_version_storage():
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
