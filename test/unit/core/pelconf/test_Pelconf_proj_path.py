# pylint: disable=missing-docstring
import pytest

from peltak import testing
from peltak.core import conf
from peltak.core import pelconf
from peltak.core import util


@testing.patch_proj_root('/fake/proj')
@pytest.mark.parametrize('proj_path,abs_path', [
    ('testfile', '/fake/proj/testfile'),
    ('sub/testfile', '/fake/proj/sub/testfile'),
    ('/abs/path', '/abs/path'),
])
def test_converts_project_path_to_an_absolute_path(proj_path, abs_path):
    # Patch project root location
    assert conf.proj_path(proj_path) == abs_path


@testing.patch_proj_root(None)
def test_returns_input_path_if_no_project_root_found():
    setattr(pelconf._find_proj_root, util.cached_result.CACHE_VAR, None)
    assert conf.proj_path('hello/world') == 'hello/world'


@testing.patch_proj_root('/fake/proj')
def test_can_join_paths():
    assert conf.proj_path('sub', 'testfile') == '/fake/proj/sub/testfile'


@testing.patch_proj_root('/fake/proj')
def test_works_with_abspath_split_into_parts():
    assert conf.proj_path('/sub', 'testfile') == '/sub/testfile'
