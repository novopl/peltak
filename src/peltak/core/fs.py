# -*- coding: utf-8 -*-
"""
File system related helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import fnmatch
import os
import re
from os.path import exists, isdir, join, normpath
from shutil import rmtree

# 3rd party imports
from six import string_types

# local imports
from . import log
from . import shell


def surround_paths_with_quotes(paths):
    """ Put quotes around all paths and join them with space in between. """
    if isinstance(paths, string_types):
        raise ValueError(
            "paths cannot be a string. "
            "Use array with one element instead."
        )
    return ' '.join('"' + path + '"' for path in paths)


def rm_glob(pattern, exclude_env=True, exclude_tox=True):
    """ Remove all files matching the given glob *pattern*. """
    log.info("Removing files matching {}", pattern)

    cmd = ['find . -name "{}"'.format(pattern)]

    if exclude_env:
        # Remove entries starting with ./env
        cmd.append("| sed '/^\.\/env/d'")

    if exclude_tox:
        # Remove entries starting with ./.tox
        cmd.append("| sed '/^\.\/\.tox/d'")

    matches = shell.run(' '.join(cmd), capture=True)

    for path in matches.stdout.splitlines():
        # might be a child of a dir deleted in an earlier iteration
        if not exists(path):
            continue

        try:
            if not isdir(path):
                log.info('  <91>[file] <90>{}', path)
                os.remove(path)
            else:
                log.info('  <91>[dir]  <90>{}', path)
                rmtree(path)
        except OSError:
            log.info("<33>Failed to remove <90>{}", path)


def filtered_walk(path, include=None, exclude=None):
    """ Walk recursively starting at *path* excluding files matching *exclude*

    :param str path:
        A starting path. This has to be an existing directory.
    :param List[str] exclude:
        A list of glob string patterns to test against. If the file/path
        matches any of those patters, it will be filtered out.
    :return:
        A generator yielding all the files that do not match any pattern in
        *exclude*.
    """
    include = include or []
    exclude = exclude or []

    if not isdir(path):
        raise ValueError("Cannot walk files, only directories")

    files = os.listdir(path)
    for name in files:
        filename = normpath(join(path, name))

        # If excluded, completely skip it. Will not recurse into directories
        if search_globs(filename, exclude):
            continue

        # If we have a whitelist and the pattern matches, yield it. If the
        # pattern didn't match and it's a dir, it will still be recursively
        # processed.
        if not include or match_globs(filename, include):
            yield filename

        if isdir(filename):
            for p in filtered_walk(filename, include, exclude):
                yield p


def match_globs(path, patterns):
    """ Test whether the given *path* matches any patterns in *excluded*

    :param str path:
        A file path to test for matches.
    :param List[str] patterns:
        A list of glob string patterns to test against. If *path* matches any
        of those patters, it will return True.
    :return bool:
        True if the *path* matches any pattern in *excluded*.
    """
    return next(
        (True for ptrn in patterns if ptrn and fnmatch.fnmatch(path, ptrn)),
        False
    )


def search_globs(path, patterns):
    """ Test whether the given *path* matches any patterns in *excluded*

    :param str path:
        A file path to test for matches.
    :param List[str] excluded:
        A list of glob string patterns to test against. If *path* matches any
        of those patters, it will return True.
    :return bool:
        True if the *path* matches any pattern in *excluded*.
    """
    for pattern in (p for p in patterns if p):
        if pattern.startswith('/'):
            # If pattern starts with root it means it match from root only
            regex = fnmatch.translate(pattern[1:])
            m = re.search(regex, path)

            if m and m.start == 0:
                return True

        else:
            regex = fnmatch.translate(pattern)
            if re.search(regex, path):
                return True

    return False
