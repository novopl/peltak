# -*- coding: utf-8 -*-
""" Helper commands for dealing with pypi. """
from __future__ import absolute_import, unicode_literals
from peltak.cli import root_cli, click


@root_cli.group('pypi')
def pypi_cli():
    # type: () -> None
    """ pypi related commands """
    pass


@pypi_cli.command('upload')
@click.argument('target')
def upload(target):
    # type: (str) -> None
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak pypi upload pypi    # Upload the current code to pypi
        $ peltak pypi upload private # Upload to pypi server 'private'

    """
    from peltak.extra.pypi import logic
    logic.upload(target)


@pypi_cli.command('configure')
@click.option(
    '-u', '--username',
    type=str,
    help="PyPi username. Defaults to PYPI_USER env variable."
)
@click.option(
    '-p', '--password',
    type=str,
    help="PyPi password. Defaults to PYPI_PASS env variable."
)
def configure(username, password):
    # type: (str, str) -> None
    """
    Generate .pypirc config with the given credentials.

    Example:

        $ peltak pypi configure my_pypi_user my_pypi_pass

    """
    from peltak.extra.pypi import logic
    logic.gen_pypirc(username, password)
