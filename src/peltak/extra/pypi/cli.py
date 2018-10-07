# -*- coding: utf-8 -*-
""" Helper commands for dealing with pypi. """
from __future__ import absolute_import, unicode_literals
from peltak.cli import cli, click


@cli.group('pypi')
def pypi_cli():
    """ pypi related commands """
    pass


@pypi_cli.command('upload')
@click.argument('target')
def upload(target):
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak pypi upload pypi    # Upload the current code to pypi
        $ peltak pypi upload private # Upload to pypi server 'private'

    """
    from peltak.extra.pypi import impl
    impl.upload(target)


@pypi_cli.command('configure')
@click.option(
    '-u', '--username',
    type=str,
    help="PyPi username"
)
@click.option(
    '-p', '--password',
    type=str,
    help="PyPi username"
)
def configure(username, password):
    """
    Generate .pypirc config with the given credentials.

    Example::

        $ peltak pypi configure my_pypi_user my_pypi_pass

    """
    from peltak.extra.pypi import impl
    impl.gen_pypirc(username, password)
