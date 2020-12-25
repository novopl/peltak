# Copyright 2017-2020 Mateusz Klos
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
.. module:: peltak.core.versioning
    :synopsis: Functionality related to project versioning.
"""
import json
import re
from collections import OrderedDict
from os.path import exists
from typing import List, Optional, Tuple

from . import conf
from . import fs
from . import util


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


def is_valid(version_str: str) -> bool:
    """ Check if the given string is a version string

    Args:
        version_str (str):
            A string to check

    Returns:
        bool: **True** if the given string is a version.
    """
    return bool(version_str and RE_VERSION.match(version_str))


def current() -> str:
    """ Return the project's current version.

    The project is read from the first file on the 'version.files' list. We
    always use the first file on the list as the source of truth, but any
    changes will be written to all files specified on the list.

    Returns:
        str: The current project version in MAJOR.MINOR.PATCH format. PATCH
        might be omitted if it's 0, so 1.0.0 becomes 1.0 and 0.1.0 becomes 0.1.
    """
    main_version_file = get_version_files()[0]
    return main_version_file.read() or ''


def write(version: str) -> None:
    """ Write the given version to the VERSION_FILE """
    if not is_valid(version):
        raise ValueError("Invalid version: '{}'".format(version))

    for version_file in get_version_files():
        version_file.write(version)


def bump(component: str = 'patch', exact: Optional[str] = None) -> Tuple[str, str]:
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


def _bump_version(version: str, component: str = 'patch') -> str:
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
        raise ValueError(
            f"Version must be in MAJOR.MINOR[.PATCH] format, got: '{version}'"
        )

    major = m.group('major')
    minor = m.group('minor') or '0'
    patch = m.group('patch') or None

    if component == 'major':
        major = str(int(major) + 1)
        minor = '0'
        patch = '0'

    elif component == 'minor':
        minor = str(int(minor) + 1)
        patch = '0'

    else:
        patch = patch or '0'
        patch = str(int(patch) + 1)

    new_ver = '{}.{}.{}'.format(major, minor, patch)

    return new_ver


class VersionFile(object):
    """ Base class for version storage.

    A version storage is a way to store the project version. Different projects
    will have different ways of storing the version. The simplest case is a
    text file that holds just the version number (probably called VERSION).
    Python projects can also use a version stored as ``__version__`` variable
    inside the project package/module. A Node.js project on the other hand will
    probably keep the version in ``package.json``. All of the above strategies
    can be (and are) implemented through subclassing this class.

    @see `PyVersionFile`, `RawVersionFile`, `NodeVersionFile`
    """
    def __init__(self, path: str) -> None:
        self.path = path
        if not exists(path):
            raise ValueError("Version file '{}' does not exist.".format(path))

    def read(self) -> Optional[str]:
        """ Read the current project version.

        All subclasses must implement this method.

        Raises:
            NotImplementedError:
                If the subclass does nto implement the read() method.
        """
        raise NotImplementedError("{} must implement .read()".format(
            self.__class__.__name__
        ))

    def write(self, version: str):
        """ Save the given version as the current project version.

        All subclasses must implement this method.

        Raises:
            NotImplementedError:
                If the subclass does nto implement the write() method.
        """
        raise NotImplementedError("{} must implement .write()".format(
            self.__class__.__name__
        ))


class PyVersionFile(VersionFile):
    """ Store project version in one of the py module/package files. """
    def read(self) -> Optional[str]:
        """ Read the project version from .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and read the version string.
        """
        with open(self.path) as fp:
            content = fp.read()
            m = RE_PY_VERSION.search(content)
            if not m:
                return None
            else:
                return m.group('version')

    def write(self, version: str):
        """ Write the project version to .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and substitute the version string
        for the new version.
        """
        with open(self.path) as fp:
            content = fp.read()

        ver_statement = "__version__ = '{}'".format(version)
        new_content = RE_PY_VERSION.sub(ver_statement, content)
        fs.write_file(self.path, new_content)


class RawVersionFile(VersionFile):
    """ Store project version as a simple value in a text file. """
    def read(self) -> Optional[str]:
        """ Read the project version from .py file.

        This will regex search in the file for a
        ``__version__ = VERSION_STRING`` and read the version string.
        """
        with open(self.path) as fp:
            version = fp.read().strip()

            if is_valid(version):
                return version

            return None

    def write(self, version: str):
        fs.write_file(self.path, version)


class NodeVersionFile(VersionFile):
    """ Store project version in package.json. """
    def read(self) -> Optional[str]:
        with open(self.path) as fp:
            config = json.load(fp)
            return config.get('version')

    def write(self, version: str):
        with open(self.path, 'r') as fp:
            config = json.load(fp, object_pairs_hook=OrderedDict)

        config['version'] = version

        fs.write_file(self.path, json.dumps(config, indent=2) + '\n')


class PyprojectTomlVersionFile(VersionFile):
    """ Store project version in package.json. """
    def read(self) -> Optional[str]:
        config = util.toml_load(self.path)
        tool_cfg = config.get('tool', {})
        poetry_cfg = tool_cfg.get('poetry')
        return poetry_cfg.get('version')
        # poetry_cfg = tool_cfg.get('poetry')
        # return config.get('tool', {}).get('poetry', {}).get('version')

    def write(self, version: str):
        config = util.toml_load(self.path)
        config['tool']['poetry']['version'] = version

        fs.write_file(self.path, util.toml_dump(config))


def get_version_files() -> List[VersionFile]:
    version_files = conf.get('version.files', [])

    if not version_files:
        single = conf.get('version.file', None)
        version_files = [single if single else 'VERSION']

    return [load_version_file(p) for p in version_files]


def load_version_file(path: str) -> VersionFile:
    """ Get version storage for the given version file.

    The storage engine used depends on the extension of the *version.file* conf
    variable.
    """
    abs_path = conf.proj_path(path)

    if abs_path.endswith('.py'):
        return PyVersionFile(abs_path)
    elif abs_path.endswith('package.json'):
        return NodeVersionFile(abs_path)
    elif abs_path.endswith('pyproject.toml'):
        return PyprojectTomlVersionFile(abs_path)
    else:
        return RawVersionFile(abs_path)
