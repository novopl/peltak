# -*- coding: utf-8 -*-
""" Helper commands for releasing to pypi. """
from __future__ import absolute_import
from . import cli, click


@cli.group('release')
def release_cli():
    """ Release related commands """
    pass


@release_cli.command()
@click.argument('target')
def upload(target):
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak release upload pypi    # Upload the current release to pypi
        $ peltak release upload private # Upload to pypi server 'private'

    """
    from peltak.commands import release
    release.upload(target)


@release_cli.command('gen-pypirc')
@click.argument('username', required=False)
@click.argument('password', required=False)
def gen_pypirc(username=None, password=None):
    """
    Generate .pypirc config with the given credentials.

    Example::

        $ peltak release gen-pypirc my_pypi_user my_pypi_pass

    """
    from peltak.commands import release
    release.gen_pypirc(username, password)
