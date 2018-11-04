# -*- coding: utf-8 -*-
""" Lint command implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
from collections import OrderedDict
from functools import wraps
from itertools import chain
from typing import List

# 3rd party imports
from six import string_types

# local imports
from peltak.core import conf
from peltak.core import fs
from peltak.core import git
from peltak.core import log
from peltak.core import shell
from peltak.core import util


g_linters = OrderedDict()


def lint(exclude, skip_untracked, commit_only, pretend):
    # type: (List[str], bool, bool, bool) -> None
    """ Lint python files.

    Args:
        exclude (list[str]):
            A list of glob string patterns to test against. If the file/path
            matches any of those patters, it will be filtered out.
        skip_untracked (bool):
            If set to **True** it will skip all files not tracked by git.
        commit_only (bool):
            Only lint files that are staged for commit.
        pretend (bool):
            If set to **True** do not actually run the checks but rather
            just show the list of files that would be linted.
    """
    runner = LintRunner(exclude, skip_untracked, commit_only, pretend)

    if not runner.run():
        exit(1)


def tool(name):
    global g_linters

    def decorator(fn):
        g_linters[name] = fn
        return fn

    return decorator


class Linter(object):
    """ Base class for integrations with 3rd party tools.

    Each linter tool should subclass this class and implement the `run` method.

    Attributes:
        retcode (Optional[int]):
            The implementation should store the return code in this attribute
            for later access. **0** means success, **None** means the tool was
            not ran yet.
    """
    name = '(unnamed linter)'

    def __init__(self):
        # type: () -> None
        self.retcode = None

    def check(self, files):
        # type; (List[str]) -> bool
        """ Check the given files.

        This is the method that need to be overridden by the subclasses. It
        should perform it's checks,  store the return code in `retcode`
        attribute and return a bool indicating if the the code passed the check.

        Args:
            files (list[str]):
                The list of files to check.

        Returns:
            bool: **True** if all files are deemed ok, **False** otherwise.
        """
        raise NotImplementedError("Subclasses must implement check() method")


class LintRunner(object):
    """ Lint runner class.

    This class represents a single linter run that includes running all the
    tools configured. It will notify the user about progress through stdout.
    """
    def __init__(self, exclude, skip_untracked, commit_only, pretend):
        # type: (List[str], bool, bool, bool) -> None
        """ Run static analysis on the given files.

        Args:
            exclude (list[str]):
                A list of glob string patterns to test against. If the file/path
                matches any of those patters, it will be filtered out.
            skip_untracked (bool):
                If set to **True** it will skip all files not tracked by git.
            commit_only (bool):
                Only lint files that are staged for commit.
            pretend (bool):
                If set to **True** do not actually run the checks but rather
                just show the list of files that would be linted.
            linters (list[Linter]):
                A list of linters to run against the code.

        Returns:
            bool: **True** if linting did not return any errors, **False**
            otherwise.
        """
        self.exclude = exclude
        self.skip_untracked = skip_untracked
        self.commit_only = commit_only
        self.pretend = pretend
        self.allow_empty = True

        self.linters = OrderedDict()
        for tool in conf.get('lint.tools', ['pep8', 'pylint']):
            if tool in g_linters:
                self.linters[tool] = g_linters[tool]
            else:
                log.err("Unknown lint tool <35>{}", tool)

    def run(self):
        """ Run all linters and report results.

        Returns:
            bool: **True** if all checks were successful, **False** otherwise.
        """
        # type: () -> bool
        with util.timed_block() as t:
            files = self._collect_files()

        # Print collected files
        if files:
            log.info("Files:")
            for p in files:
                log.info("  <0>{}", p)
        else:
            log.err("No files found for linting, exiting...")
            return self.allow_empty

        log.info("Collected <33>{} <32>files in <33>{}s".format(
            len(files), t.elapsed_s
        ))

        success = True
        if not self.pretend:
            results = OrderedDict()

            with util.timed_block() as t:
                for name, check_fn in self.linters.items():
                    log.info("Running <35>{}".format(name))
                    results[name] = check_fn(files)

            log.info("Code checked in <33>{}s", t.elapsed_s)

            for name, retcode in results.items():
                if retcode != 0:
                    success = False
                    log.err("<35>{} <31>failed with return code: <33>{}".format(
                        name, retcode
                    ))

        return success

    def _collect_files(self):
        # type: () -> List[str]
        paths = [conf.proj_path(p) for p in conf.get('lint.paths', [])]
        exclude = list(self.exclude)
        exclude = exclude or conf.get('lint.exclude', [])

        # prepare
        if self.commit_only:
            include = ['*' + f for f in git.staged() if f.endswith('.py')]
            exclude += git.ignore()
        else:
            include = ['*.py']

        if self.skip_untracked:
            exclude += git.untracked()

        if isinstance(paths, string_types):
            raise ValueError("paths must be an array of strings")

        log.info("Paths to lint:")
        for path in paths:
            log.info("  <0>{}", path)

        return list(chain.from_iterable(
            fs.filtered_walk(p, include, exclude) for p in paths
        ))


@tool('pep8')
def pep8_check(files):
    # type: (List[str]) -> int
    files = fs.surround_paths_with_quotes(files)
    cfg_path = conf.get_path('lint.pep8_cfg', 'ops/tools/pep8.ini')
    pep8_cmd = 'pep8 --config {} {}'.format(cfg_path, files)

    return shell.run(pep8_cmd, exit_on_error=False).return_code


@tool('pylint')
def pylint_check(files):
    # type: (List[str]) -> int
    files = fs.surround_paths_with_quotes(files)
    cfg_path = conf.get_path('lint.pylint_cfg', 'ops/tools/pylint.ini')
    pylint_cmd = 'pylint --rcfile {} {}'.format(cfg_path, files)

    return shell.run(pylint_cmd, exit_on_error=False).return_code


# Used in docstrings only until we drop python2 support
del List
