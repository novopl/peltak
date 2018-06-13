# -*- coding: utf-8 -*-
"""
Code linting commands.
"""
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from six import string_types
from fabric.api import local

# local imports
from .common import conf
from .common import fs
from .common import log


PYLINT_CFG_PATH = conf.get_path('PYLINT_CFG_PATH', 'ops/tools/pylint.ini')
PEP8_CFG_PATH = conf.get_path('PEP8_CFG_PATH', 'ops/tools/pep8.ini')
LINT_PATHS = conf.get('LINT_PATHS', [])


def _lint_files(paths):
    """ Run static analysis on the given files.

    :param paths:   Iterable with each item being path that should be linted..
    """
    if isinstance(paths, string_types):
        raise ValueError("paths must be an array of strings")

    log.info("Linting")
    for path in paths:
        print("--   {}".format(path))

    paths = fs.surround_paths_with_quotes(paths)

    log.info("Checking PEP8 compatibility")
    pep8_cmd = 'pep8 --config {} {{}}'.format(PEP8_CFG_PATH)
    pep8_ret = local(pep8_cmd.format(paths)).return_code

    log.info("Running linter")
    pylint_cmd = 'pylint --rcfile {} {{}}'.format(PYLINT_CFG_PATH)
    pylint_ret = local(pylint_cmd.format(paths)).return_code

    if pep8_ret != 0:
        print("pep8 failed with return code {}".format(pep8_ret))

    if pylint_ret:
        print("pylint failed with return code {}".format(pylint_ret))

    return pep8_ret == pylint_ret == 0


def lint():
    """ Run pep8 and pylint on all project files. """
    if not _lint_files([conf.proj_path(p) for p in LINT_PATHS]):
        exit(1)
