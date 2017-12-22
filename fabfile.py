# -*- coding: utf-8 -*-
"""
This is fabrics configuration file.
"""
from __future__ import absolute_import

# Configure the build
from fabops.commands.common import conf
conf.init({
    'SRC_DIR': '.',
    'SRC_PATH': 'fabops/commands',
    'BUILD_DIR': '.build',
    'LINT_PATHS': [
        'fabops/commands',
    ],
    'REFDOC_PATHS': [
        'fabops/commands',
    ],
    'TEST_TYPES': {
        'default': {'paths': [
            'fabops/commands',
            'test/unit'
        ]}
    },
})


# Import all commands
from fabops.commands.clean import *
from fabops.commands.docs import *
from fabops.commands.git import *
from fabops.commands.lint import *
from fabops.commands.release import *
from fabops.commands.test import *
