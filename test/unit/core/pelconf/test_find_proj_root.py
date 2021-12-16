# pylint: disable=missing-docstring
# TODO: Add tests based on real files. Mocking all the scanning through
#  directory sucks. Better to just create a few project directories as
#  test data and execute operations on them.
from functools import wraps
from os.path import join
from unittest.mock import Mock, patch

from peltak.core import conf


class patch_pelconf_location(object):
    """ Patch project root decorator. """
    def __init__(self, proj_root, nest_level=0):
        self.proj_root = proj_root
        self.nest = nest_level

    def __call__(self, fn):
        if self.proj_root is not None:
            cwd = join(self.proj_root, *(['fake_dir'] * self.nest))
            dirs = ['not_pelconf'] * self.nest + [conf.DEFAULT_PELCONF_NAME]
            dirs = [[d] for d in dirs]
        else:
            cwd = join('/', *(['fake_dir'] * self.nest))
            dirs = [[d] for d in ['not_pelconf'] * self.nest]

        @patch('os.getcwd', Mock(return_value=cwd))
        @patch('os.listdir', Mock(side_effect=dirs))
        @wraps(fn)
        def wrapper(*args, **kw):       # pylint: disable=missing-docstring
            return fn(*args, **kw)

        return wrapper


@patch_pelconf_location('/fake/proj/root')
def test_runs_detection_when_no_global_variable_stored():
    assert conf._discover_proj_config() == '/fake/proj/root/pelconf.yaml'


@patch_pelconf_location(None)
def test_returns_none_if_not_found():
    assert conf._discover_proj_config() is None


def test_fake():
    pass
