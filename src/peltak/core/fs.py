# -*- coding: utf-8 -*-
"""
File system related helpers.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import exists, join, isdir
from shutil import rmtree
from fnmatch import fnmatch

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

        if not isdir(path):
            log.info('  ^91[file] ^90{}'.format(path))
            os.remove(path)
        else:
            log.info('  ^91[dir]  ^90{}'.format(path))
            rmtree(path)


def filtered_walk(path, exclude):
    if not isdir(path):
        raise ValueError("Cannot walk files, only directories")

    files = os.listdir(path)
    for name in files:
        file_path = join(path, name)

        if is_excluded(name, file_path, exclude):
            continue

        yield name, file_path

        if isdir(file_path):
            for n, p in filtered_walk(file_path, exclude):
                yield n, p


def is_excluded(name, path, excluded):
    matches = lambda pattern: fnmatch(name, pattern) or fnmatch(path, pattern)
    return next((True for x in excluded if matches(x)), False)
