# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
import pytest

# local imports
from peltak.core import git
from peltak import testing


@pytest.mark.skip(
    'git.num_commits() is deprecated by CommitDetails.get().number'
)
@testing.patch_run('\n'.join([
    'commit1',
    'commit2',
    'commit3',
    'commit4',
    'commit5',
]))
def test_works():
    assert git.num_commits() == 5
