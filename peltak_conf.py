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
from peltak.commands.common import conf
conf.init({
    'SRC_DIR': 'src',
    'SRC_PATH': 'src/peltak',
    'BUILD_DIR': '.build',
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
from peltak.commands.clean import *
from peltak.commands.docs import *
from peltak.commands.git import *
from peltak.commands.lint import *
from peltak.commands.ops import *
from peltak.commands.release import *
from peltak.commands.test import *
