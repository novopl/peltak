# -*- coding: utf-8 -*-
"""
This is fabrics configuration file.
"""
from __future__ import absolute_import

# Add src to PYTHONPATH
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, join(abspath(dirname(__file__)), 'src'))


# Configure the build
from fabops.commands.common import conf
conf.init({
    'SRC_DIR': 'src',
    'SRC_PATH': 'src/fabops',
    'BUILD_DIR': '.build',
    'LINT_PATHS': [
        'src/fabops',
    ],
    'REFDOC_PATHS': [
        'src/fabops',
    ],
    'TEST_TYPES': {
        'default': {'paths': [
            'src/fabops',
            'test/unit'
        ]}
    },
})


# Import all commands
from fabops.commands.clean import *
from fabops.commands.docs import *
from fabops.commands.git import *
from fabops.commands.lint import *
from fabops.commands.ops import *
from fabops.commands.release import *
from fabops.commands.test import *
