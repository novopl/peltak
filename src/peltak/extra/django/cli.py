# -*- coding: utf-8 -*-
"""
Django related management commands.

Those commands replace the usage of ``./manage.py`` (thus it's removed). Those
correspond 1 to 1 to their ``./manage.py`` counterparts. Those commands mainly
exists so that manage.py can be deleted (less top-level files in project dir).
"""
from __future__ import absolute_import

from peltak.cli import root_cli, click


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
def devserver(port=8000, settings=None):
    # type: (int, str) -> None
    """ Run dev server. """
    _manage_cmd(['runserver', '0.0.0.0:{}'.format(port)], settings)


@django_cli.command('collectstatic')
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

    sys.path.insert(0, conf.get('src_dir'))

    settings = settings or conf.get('django.settings', None)
    environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

    from django.core.management import execute_from_command_line

    args = sys.argv[0:-1] + cmd

    execute_from_command_line(args)
