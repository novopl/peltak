# -*- coding: utf-8 -*-
"""
Various commands that do not fit another category but there's not enough of them
to justify a separate module.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
import os.path
import shutil

# 3rd party imports
from fabric.api import local, lcd
from refdoc import generate_docs as _generate_docs

# local imports
from .common import conf
from .common import log


BUILD_DIR = conf.get_path('BUILD_DIR', '.build')
DOC_SRC_PATH = conf.get_path('DOC_SRC_PATHS', 'docs')
REFDOC_PATHS = conf.get('REFDOC_PATHS', [])

DOC_OUT_PATH = os.path.join(DOC_SRC_PATH, 'html')
DOC_REF_PATH = os.path.join(DOC_SRC_PATH, 'ref')
DOC_ASSETS_PATH = os.path.join(DOC_SRC_PATH, 'assets')
DOC_BUILD_PATH = os.path.join(BUILD_DIR, 'docs')


def docs(recreate='no', no_index='false'):
    """ Build project documentation. """
    log.info('Ensuring assets directory ^94{}^32 exists', DOC_ASSETS_PATH)
    if not os.path.exists(DOC_ASSETS_PATH):
        os.makedirs(DOC_ASSETS_PATH)

    if conf.is_true(recreate) and os.path.exists(DOC_OUT_PATH):
        log.info("^91Deleting ^94{}".format(DOC_OUT_PATH))
        shutil.rmtree(DOC_OUT_PATH)

    if DOC_REF_PATH:
        _gen_ref_docs(DOC_REF_PATH, conf.is_true(no_index))
    else:
        log.err('Not generating any reference documentation - '
                'No DOC_REF_PKG_PATHS specified in config')

    with lcd(DOC_SRC_PATH):
        log.info('Building docs with ^35sphinx')
        local('sphinx-build -b html -d {build} {docs} {out}'.format(
            build=DOC_BUILD_PATH,
            docs=DOC_SRC_PATH,
            out=DOC_OUT_PATH,
        ))


def _gen_ref_docs(ref_path, no_index=False):
    log.info('Removing previously generated reference documentation')
    if os.path.exists(ref_path):
        shutil.rmtree(ref_path)

    os.makedirs(ref_path)

    log.info('Generating reference documentation')
    args = {'out_dir': ref_path}

    if no_index:
        args['no_index'] = True

    pkg_paths = [conf.proj_path(p) for p in REFDOC_PATHS]

    _generate_docs(pkg_paths, **args)


def _collect_commands():
    # pylint: disable=unused-variable
    from fabops.commands import appengine
    from fabops.commands import clean
    from fabops.commands import django
    from fabops.commands import docs
    from fabops.commands import frontend
    from fabops.commands import git
    from fabops.commands import ops
    from fabops.commands import release
    from fabops.commands import test
    import fabops.commands as fabops_cmds
    from types import ModuleType

    commands = {}
    modules = [
        m for m in fabops_cmds.__dict__.values()
        if isinstance(m, ModuleType)
    ]

    commands = []
    for module in modules:
        commands += [
            attr for attr_name, attr in module.__dict__.items()
            if (
                callable(attr) and
                attr_name[0] != '_' and
                attr.__module__ == module.__name__
            )
        ]

    return {cmd.__name__: cmd for cmd in commands}

    return commands


def help(command=None):     # pylint: disable=redefined-builtin
    """ Simple help system for commands """
    from rst2ansi import rst2ansi

    commands = _collect_commands()

    if command is None:
        help_text = [
            'To get help for a specific command:',
            '  \033[90mfab help:<command_name>\033[0m',
            '',
            'Example:',
            '  \033[90mfab help:lint\033[0m',
            '',
            'Here is a list of all fabops commands (some might not be enabled'
            ' for the project):\n  - ' + '\n  - '.join(commands.keys()),
        ]
        print('\n'.join(help_text))
    elif command not in commands:
        print("Command not found")
    else:
        cmd = commands[command]
        docs = cmd.__doc__.encode('utf-8')

        print('\033[1m-' * 80)
        print('{}\033[0m\n'.format(command))
        print(rst2ansi(docs))
