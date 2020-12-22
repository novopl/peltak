# pylint: disable=missing-docstring
from peltak import testing
from peltak.core import git


FAKE_GIT_STATUS = '\n'.join([
    'D  deleted.txt',
    ' M unstaged.txt',
    'M  staged.txt',
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
def test_returns_untracked_files_properly(app_conf):
    assert frozenset(git.untracked()) == frozenset([
        'untracked_1.txt',
        'untracked_2.txt',
        'untracked_3.txt',
        'untracked_4.txt',
    ])
