# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# 3rd party imports
from mock import patch

# local imports
from peltak.core import conf


@patch('os.chdir')
@patch('os.getcwd')
def test_works_as_expected(p_getcwd, p_chdir):       # Better one test than none
    fake_cwd = 'fake_dir'
    path = '.'

    p_getcwd.return_value = fake_cwd

    with conf.within_proj_dir(path):
        p_getcwd.assert_called()
        p_chdir.assert_called_once_with(conf.proj_path(path))

    # last call was back to our fake working directory
    p_chdir.assert_called_with(fake_cwd)
