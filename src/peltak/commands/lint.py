# -*- coding: utf-8 -*-
"""
Code linting commands.
"""
from __future__ import absolute_import, unicode_literals
from . import cli


def _lint_files(paths):
    """ Run static analysis on the given files.

    :param paths:   Iterable with each item being path that should be linted..
    """
    from six import string_types
    from peltak.core import conf
    from peltak.core import fs
    from peltak.core import log
    from peltak.core import shell

    pylint_cfg_path = conf.get_path('PYLINT_CFG_PATH', 'ops/tools/pylint.ini')
    pep8_cfg_path = conf.get_path('PEP8_CFG_PATH', 'ops/tools/pep8.ini')

    if isinstance(paths, string_types):
        raise ValueError("paths must be an array of strings")

    log.info("Linting")
    for path in paths:
        print("--   {}".format(path))

    paths = fs.surround_paths_with_quotes(paths)

    log.info("Checking PEP8 compatibility")
    pep8_cmd = 'pep8 --config {} {{}}'.format(pep8_cfg_path)
    pep8_ret = shell.run(pep8_cmd.format(paths)).return_code

    log.info("Running linter")
    pylint_cmd = 'pylint --rcfile {} {{}}'.format(pylint_cfg_path)
    pylint_ret = shell.run(pylint_cmd.format(paths)).return_code

    if pep8_ret != 0:
        print("pep8 failed with return code {}".format(pep8_ret))

    if pylint_ret:
        print("pylint failed with return code {}".format(pylint_ret))

    return pep8_ret == pylint_ret == 0


@cli.command()
def lint():
    """ Run pep8 and pylint on all project files. """
    from peltak.core import conf

    lint_paths = conf.get('LINT_PATHS', [])

    if not _lint_files([conf.proj_path(p) for p in lint_paths]):
        exit(1)
