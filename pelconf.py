# -*- coding: utf-8 -*-
""" peltak configuration file.

See `peltak <https://github.com/novopl/peltak>`_ for more information.
"""
from __future__ import absolute_import

# Add src to PYTHONPATH
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, join(abspath(dirname(__file__)), 'src'))


# Configure the build
from peltak.core import conf

conf.init({
    'DOCKER_REGISTRY': 'docker.novocode.net',
    'SRC_DIR': 'src',
    'SRC_PATH': 'src/peltak',
    'BUILD_DIR': '.build',
    'VERSION_FILE': 'src/peltak/__init__.py',
    'LINT_PATHS': [
        'src/peltak',
    ],
    'REFDOC_PATHS': [
        'src/peltak',
    ],
    'TEST_TYPES': {
        'default': {'paths': [
            'src/peltak',
            'test/unit'
        ]}
    },
})

# Import all commands
from peltak.commands import appengine
from peltak.commands import django
from peltak.commands import docker
from peltak.commands import docs
from peltak.commands import frontend
from peltak.commands import git
from peltak.commands import lint
from peltak.commands import release
from peltak.commands import test
from peltak.commands import version
