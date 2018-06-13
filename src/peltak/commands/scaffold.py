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

# local imports
from peltak.core import log
from peltak.core.template import Scaffold
from . import cli


TEMPLATE_LINE_SEP = '\n'
TEMPLATE_CONFIG_FILE = 'peltak-template-config.json'
NAME_MARKER = '_PELTAK-SCAFFOLD-NAME_'


@cli.group()
def scaffold():
    """ Project scaffold related commands. """
    pass


@scaffold.command()
@click.argument(
    'src_dir',
    type=click.Path(file_okay=False, dir_okay=True, exists=True)
)
@click.option('--name', 'template_name', type=str)
@click.option('-e', '--exclude', multiple=True, metavar='PATTERN')
def create(src_dir, template_name, exclude):
    log.info("Creating scaffold ^35{}".format(template_name))
    log.info("Exclude: {}".format(exclude))

    scaffold = Scaffold.create(src_dir, template_name, exclude)
    scaffold.write('.')


@scaffold.command()
@click.option('-t', '--template', type=str, required=True)
def info(template):
    scaffold = Scaffold.load(template)

    log.info("Name:     ^33{}", scaffold.name)
    log.info("Size:     ^33{} kb", round(scaffold.size / 1024))

    log.info("Marked files:")
    for path in scaffold.marked_files:
        log.info('  ^90{}', path)


@scaffold.command()
@click.argument('name', type=str)
@click.option('-t', '--template', type=str, required=True)
def apply(template, name):
    scaffold = Scaffold.load(template)
    scaffold.apply(name, '.')
