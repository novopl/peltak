# -*- coding: utf-8 -*-
# Copyright 2017-2018 Mateusz Klos
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
"""
Django related management commands.

Those commands replace the usage of ``./manage.py`` (thus it's removed). Those
correspond 1 to 1 to their ``./manage.py`` counterparts. Those commands mainly
exists so that manage.py can be deleted (less top-level files in project dir).
"""
from __future__ import absolute_import

from peltak.commands import root_cli, click, pretend_option
from peltak.core import conf


conf.command_requirements(
    'django~=1.11'
)


@root_cli.group('django')
def django_cli():
    # type: () -> None
    """ Commands related to django """
    pass


@django_cli.command('devserver')
@click.option(
    '-p', '--port',
    type=int,
    default=8000,
    help="Port the server will run on"
)
@click.option(
    '-s', '--settings',
    type=str,
    help="Settings module to use. Defaults to DJANGO_SETTINGS conf variable."
)
@pretend_option
def devserver(port=8000, settings=None):
    # type: (int, str) -> None
    """ Run dev server. """
    _manage_cmd(['runserver', '0.0.0.0:{}'.format(port)], settings)


@django_cli.command('collectstatic')
@pretend_option
def collectstatic():
    # type: () -> None
    """ Collect all static files.

    This command won't ask for permission as manage.py does.

    Sample Config::

        \b
        src_dir: 'src'
        django:
          settings: 'mypkg.settings'

    Example::

        $ peltak django collectstatic

    """
    _manage_cmd(['collectstatic', '--no-input'])


@django_cli.command('mkmigrations')
@click.argument('app')
@click.argument('name')
@pretend_option
def mkmigrations(app, name):
    # type: (str, str) -> None
    """ Create a named migration for a given app.

    This will require the user to name every migration he creates thus improving
    the source code. Otherwise it's just a simple wrapper around ./manage.py.

    Sample Config::

        \b
        src_dir: 'src'
        django:
          settings: 'mypkg.settings'

    Example::

        $ peltak django mkmigrations mypkg.app add_new_fields_to_mytable

    """
    _manage_cmd(['makemigrations', '-n', name] + app.split(' '))


@django_cli.command('migrate')
@pretend_option
def migrate():
    # type: () -> None
    """ Apply pending migrations.

    Sample Config::

        \b
        src_dir: 'src'
        django:
          settings: 'mypkg.settings'

    Example::

        $ peltak django migrate

    """
    _manage_cmd(['migrate'])


@django_cli.command('createsuperuser')
@pretend_option
def createsuperuser():
    """ Create super user (probably needed for the first user).

    Sample Config::

        \b
        src_dir: 'src'

        django:
          settings: 'mypkg.settings'

    Example::

        $ peltak django createsuperuser

    """
    _manage_cmd(['createsuperuser'])


@django_cli.command('shell')
@pretend_option
def shell():
    # type: () -> None
    """ Start django shell

    Sample Config::

        \b
        src_dir: 'src'
        django:
          settings: 'mypkg.settings'

    Example::

        $ peltak django shell

    """
    _manage_cmd(['shell'])


def _manage_cmd(cmd, settings=None):
    # type: () -> None
    """ Run django ./manage.py command manually.

    This function eliminates the need for having ``manage.py`` (reduces file
    clutter).
    """
    import sys
    from os import environ
    from peltak.core import conf
    from peltak.core import context
    from peltak.core import log

    sys.path.insert(0, conf.get('src_dir'))

    settings = settings or conf.get('django.settings', None)
    environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    args = sys.argv[0:-1] + cmd

    if context.get('pretend', False):
        log.info("Would run the following manage command:\n<90>{}", args)
    else:
        from django.core.management import execute_from_command_line
        execute_from_command_line(args)
