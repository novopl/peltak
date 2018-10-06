# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals


from peltak.core import git
from peltak import testing


@testing.patch_run('\n'.join([
    'commit1',
    'commit2',
    'commit3',
    'commit4',
    'commit5',
]))
def test_works():
    assert git.num_commits() == 5
