# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import
from __future__ import absolute_import, unicode_literals


# Those modules artificially lower the coverage report stats. The code here
# will probably never be tested as those are pure usages of the click library.
# Testing this code would be testing click and not peltak. Just importing them
# so they don't appear as 0% as if it's not tested (should be 100% but let's
# settle at whatever only importing them gives us).
from peltak.commands import git
from peltak.commands import root
from peltak.commands import version
from peltak.extra import changelog
from peltak.extra import gitflow
from peltak.extra.gitflow.commands import task
from peltak.extra import pypi
from peltak.extra import scripts


def test_does_not_lower_the_coverage():
    pass
