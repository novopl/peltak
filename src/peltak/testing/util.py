""" Various utilities to help write tests for peltak. """
import os
import shutil
import tempfile
from contextlib import contextmanager
from os.path import basename, join


class DataLoader(object):
    """ Provides a temporary copy of the selected test project. """

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.proj_dir = None

    @contextmanager
    def __call__(self, path):
        work_dir = os.getcwd()

        temp_dir = tempfile.mkdtemp(prefix='peltak_tests_')
        self.proj_dir = join(temp_dir, basename(path))
        proj_src = join(self.data_dir, path)

        shutil.copytree(proj_src, self.proj_dir)
        os.chdir(self.proj_dir)

        try:
            yield self
        finally:
            os.chdir(work_dir)
            shutil.rmtree(temp_dir)
