# pylint: disable=missing-docstring
import pytest

from peltak import testing
from peltak.core import git


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
