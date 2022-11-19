# Copyright 2017-2020 Mateusz Klos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
""" Helper commands for dealing with pypi. """
from peltak.cli import click, peltak_cli, pretend_option


@peltak_cli.group('pypi')
def pypi_cli():
    """ pypi related commands """
    pass


@pypi_cli.command('upload')
@click.argument('target', required=False, default='pypi')
@pretend_option
def upload(target: str):
    """ Upload to a given pypi target.

    Examples::

        \b
        $ peltak pypi upload         # Upload the current code to pypi
        $ peltak pypi upload private # Upload to pypi target 'private'

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
@pretend_option
def configure(username: str, password: str):
    """
    Generate .pypirc config with the given credentials.

    Example:

        $ peltak pypi configure my_pypi_user my_pypi_pass

    """
    from peltak.extra.pypi import logic
    logic.gen_pypirc(username, password)
