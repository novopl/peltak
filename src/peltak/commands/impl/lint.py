# -*- coding: utf-8 -*-
""" Lint command implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from itertools import chain
from six import string_types

# local imports
from peltak.core import conf
from peltak.core import fs
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from peltak.core import util


def _lint_files(paths, include=None, exclude=None, pretend=False):
    """ Run static analysis on the given files.

    :param paths:   Iterable with each item being path that should be linted..
    """

    pylint_cfg_path = conf.get_path('PYLINT_CFG_PATH', 'ops/tools/pylint.ini')
    pep8_cfg_path = conf.get_path('PEP8_CFG_PATH', 'ops/tools/pep8.ini')

    if isinstance(paths, string_types):
        raise ValueError("paths must be an array of strings")

    log.info("Paths to lint:")
    for path in paths:
        log.info("  <0>{}", path)

    with util.timed_block() as t:
        files = list(chain.from_iterable(
            fs.filtered_walk(p, include, exclude) for p in paths
        ))

    log.info("Files:")
    for p in files:
        log.info("  <0>{}", p)

    log.info("Collected <33>{} <32>files in <33>{}s".format(
        len(files), t.elapsed_s
    ))

    if not pretend:
        log.info("Checking PEP8 compatibility")
        files = fs.surround_paths_with_quotes(files)

        with util.timed_block() as t:
            pep8_cmd = 'pep8 --config {} {}'.format(pep8_cfg_path, files)
            pep8_ret = shell.run(pep8_cmd).return_code

            log.info("Running linter")
            pylint_cmd = 'pylint --rcfile {} {}'.format(pylint_cfg_path, files)
            pylint_ret = shell.run(pylint_cmd).return_code

        log.info("Code checked in <33>{}s", t.elapsed_s)

        if pep8_ret != 0:
            log.info("pep8 failed with return code {}", pep8_ret)

        if pylint_ret:
            log.info("pylint failed with return code {}", pylint_ret)

        return pep8_ret == pylint_ret == 0

    return True


def lint(exclude, include_untracked, commit_only, pretend):
    """ Lint python files.

    TODO: Introduce a test runner interface to allow support for arbitrary tools
    """
    paths = [conf.proj_path(p) for p in conf.get('LINT_PATHS', [])]
    exclude = list(exclude)     # Convert from tuple to easily concatenate.

    if commit_only:
        include = ['*' + f for f in git.staged() if f.endswith('.py')]
        exclude += git.ignore()
    else:
        include = ['*.py']

    if not include_untracked:
        exclude += git.untracked()

    if not _lint_files(paths, include, exclude, pretend):
        exit(1)