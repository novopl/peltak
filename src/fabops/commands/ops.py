# -*- coding: utf-8 -*-
"""
Commands related directly to fabops.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import os.path

# 3rd party imports
from fabric.api import lcd, local

# local imports
from .common import conf
from .common import git
from .common import log
from .common import project


def ops_update():
    """ Pull fabops-commands mainstream updates and merge with local. """
    commands_path = os.path.dirname(__file__)

    if git.is_dirty(commands_path):
        log.err("commands repo is dirty, aborting.")
        return

    with lcd(commands_path):
        branch = git.current_branch()

        log.info("Checking out ^33master")
        local('git checkout master')

        log.info("Pulling latest changes")
        local('git pull origin master')

        log.info("Checking out ^33".format(branch))
        local('git checkout {}'.format(branch))

        log.info("Merging mainstream changes into ^33".format(branch))
        local('git merge master --no-edit')

        log.info("Done")


def seed_ops_configs(out_dir='ops', force='false'):
    """ Create initial ops configuration. """
    force = conf.is_true(force)

    with project.inside():
        configs_path = os.path.join(out_dir, 'tools')

        if not os.path.exists(configs_path):
            os.makedirs(configs_path)

        config_files = {
            'tools/coverage.ini': coverage_ini,
            'tools/pep8.ini': pep8_ini,
            'tools/pylint.ini': pylint_ini,
            'tools/pytest.ini': pytest_ini,
            'devrequirements.txt': devrequirements_txt,
        }

        for path, content in config_files.items():
            path = os.path.join(out_dir, path)

            if not os.path.exists(path) or force:
                log.info('Writing ^94{}'.format(path))
                with open(path, 'w') as fp:
                    fp.write(content)


coverage_ini = '''
[run]
branch = True
'''.lstrip()


pep8_ini = '''
[pep8]
max-line-length = 80
ignore = E221,E241,E251,W293
count = True
exclude = .ropeproject,
          env,
          local,
          docs,
'''.lstrip()


pylint_ini = '''
[MASTER]
jobs = 1

[MESSAGES CONTROL]
disable = all
enable = dangerous-default-vaulue,
         missing-docstring,
         redefined-builtin,
         unused-variable,
         unused-import,
         unsubscriptable-object,
         unused-wildcard-import,
         unreachable-code,
         wildcard-import,
         wrong-import-order

[REPORTS]
output-format = colorized
reports = no
'''.lstrip()


pytest_ini = '''
[pytest]
addopts = --durations=3
'''.lstrip()


devrequirements_txt = '''
coverage==4.2
Fabric3==1.12.post1
fabops==0.9.9
factory-boy==2.8.1
mock==2.0.0
pep8==1.7.0
pylint==1.7.4
pytest==3.2.3
pytest-cov==2.5.1
pytest-sugar==0.9.0
sphinx-refdoc==0.0.15
sphinx_rtd_theme>=0.2.4
tox==2.9.1
wheel==0.29.0
'''.lstrip()
