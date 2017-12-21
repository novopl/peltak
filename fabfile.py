# -*- coding: utf-8 -*-
"""
This is fabrics configuration file.
"""
from __future__ import absolute_import

# Configure the build
from ops.commands.common import conf
conf.init({
    'SRC_DIR': '.',
    'SRC_PATH': 'ops/commands',
    'BUILD_DIR': '.build',
    'LINT_PATHS': [
        'ops/commands',
    ],
    'REFDOC_PATHS': [
        'ops/commands',
    ],
    'TEST_TYPES': {
        'default': {'paths': [
            'ops/commands',
            'test/unit'
        ]}
    }
})


# Import all commands
from ops.commands.clean import *
from ops.commands.docs import *
from ops.commands.git import *
from ops.commands.lint import *
from ops.commands.release import *
from ops.commands.test import *
