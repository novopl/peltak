# pylint: disable=missing-docstring
from peltak import testing
from peltak.core import git


FAKE_GIT_STATUS = '\n'.join([
    'D  deleted.txt',
    ' M unstaged.txt',
    'M  staged_1.txt',
    'M  staged_2.txt',
    'R  from/renamed_1.txt -> to/renamed_1.txt',
    'R  from/renamed_2.txt -> to/renamed_2.txt',
    'RM from/renamed_and_modified_1.txt -> to/renamed_and_modified_1.txt',
    'RM from/renamed_and_modified_2.txt -> to/renamed_and_modified_2.txt',
    'RM from/renamed_and_modified_3.txt -> to/renamed_and_modified_3.txt',
    '?? untracked_1.txt',
    '?? untracked_2.txt',
    '?? untracked_3.txt',
    '?? untracked_4.txt',
])


@testing.patch_run(stdout=FAKE_GIT_STATUS)
def test_returns_staged_files_properly():
    assert frozenset(git.staged()) == frozenset([
        'deleted.txt',
        'staged_1.txt',
        'staged_2.txt',
    ])
