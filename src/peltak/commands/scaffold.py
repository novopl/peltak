# -*- coding: utf-8 -*-
"""
TODO:
    - Add optional fields.
        - On creating you specify pairs of name_in_src=field_name, The marker
          must include the field name somehow.
        - On applying during the read, once a marker is encountered the first
          time, the user us prompted for the value. Then that value is used
          for all subsequent occurrences.
"""
from __future__ import absolute_import, unicode_literals

import json
from os.path import abspath, basename
try:
    # python 3
    from io import BytesIO
except ImportError:
    # python 2
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

# 3rd party imports
import click
from six import string_types

# local imports
from peltak.core import log
from peltak.core import git
from peltak.core.scaffold import LocalStore, Scaffold
from . import cli


DirPath = click.Path(file_okay=False, dir_okay=True, exists=True)


def marker_def(string):
    name, value = string.split('=')
    name = name.strip()
    value = value.strip()

    if ',' in value:
        value = value.split(',')

    return (name, value)


@cli.group()
def scaffold():
    """ Project scaffold related commands. """
    pass


@scaffold.command()
@click.argument('src_dir', type=DirPath)
@click.option('-n', '--name', type=str)
@click.option('-e', '--exclude', multiple=True, metavar='PATTERN')
@click.option('-m', '--marker', 'markers', type=marker_def, multiple=True, metavar='NAME=VALUE(S)')
@click.option('--no-gitignore', is_flag=True)
def create(src_dir, name, markers, exclude, no_gitignore):
    store = LocalStore()

    markers = dict(markers)
    markers.setdefault('name', basename(abspath(src_dir)))

    if not no_gitignore:
        git_exclude = git.load_gitignore(src_dir)
        exclude = set(exclude) | set(git_exclude) | {'.git'}

    if name is None:
        name = markers['name']
        if not isinstance(name, string_types):
            name = name[0]      # name is a list of names, pick the first one.

    log.info("Creating scaffold ^35{}".format(name))
    log.info("Excluding")
    for pattern in exclude:
        log.info("  ^0- {}", pattern)

    scaffold = Scaffold.create(src_dir, name, exclude, markers)
    store.add(scaffold)


@scaffold.command()
@click.argument('name', type=str, required=True)
@click.option('-f', '--files', 'show_files', is_flag=True)
@click.option('-c', '--config', 'show_config', is_flag=True)
def info(name, show_files, show_config):
    store = LocalStore()
    scaffold = store.load(name)
    # scaffold = Scaffold.load_from_file(name)

    log.info("Name:     ^33{}", scaffold.name)
    log.info("Size:     ^33{} kb", round(scaffold.size / 1024))
    log.info("Created:  ^33{}", scaffold.pretty_created)

    if show_config:
        log.cprint("Config: {")
        for key, value in scaffold.json_config.items():
            log.cprint('  "{name}": ^33{value}^0'.format(
                name=key, value=json.dumps(value, indent=2)
            ))

        log.cprint("}")
        #
        # log.info("Config: ^90{}".format(
        #     json.dumps(scaffold.json_config, indent=2)
        # ))

    if show_files:
        log.info("Files:")
        for path in scaffold.files:
            if path in scaffold.marked_files:
                log.info('  ^0{}', path)
            else:
                log.info('  ^90{}', path)


@scaffold.command()
@click.argument('name', type=str, required=True)
def delete(name):
    log.info("Deleting ^35{}".format(name))
    store = LocalStore()
    store.delete(name)


@scaffold.command()
def list():
    store = LocalStore()

    log.cprint("^32Local:\n^0")
    for scaffold in store.scaffolds:
        log.cprint("  ^90{}  ^0{}", scaffold.pretty_created, scaffold.name)

    log.cprint('')


@scaffold.command()
@click.argument('name', type=str)
@click.argument('proj_name', type=str)
@click.option('-p', '--path', type=DirPath, default='.')
def apply(name, proj_name, path):
    store = LocalStore()
    scaffold = store.load(name)
    scaffold.apply(proj_name, path)
