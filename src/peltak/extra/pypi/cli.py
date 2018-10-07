# -*- coding: utf-8 -*-
""" Helper commands for dealing with pypi. """
from __future__ import absolute_import, unicode_literals
from peltak.cli import cli, click


@cli.group('pypi')
def pypi_cli():
    """ pypi related commands """
    pass


@pypi_cli.command()
@click.argument('target')
def upload(target):
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak pypi upload pypi    # Upload the current code to pypi
        $ peltak pypi upload private # Upload to pypi server 'private'

    """
    from peltak.commands import impl
    impl.upload(target)


@pypi_cli.command('gen-pypirc')
@click.argument('username', required=False)
@click.argument('password', required=False)
def gen_pypirc(username=None, password=None):
    """
    Generate .pypirc config with the given credentials.

    Example::

        $ peltak pypi gen-pypirc my_pypi_user my_pypi_pass

    """
    from . import impl
    impl.gen_pypirc(username, password)
