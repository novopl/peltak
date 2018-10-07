# -*- coding: utf-8 -*-
"""
Django related management commands.

Those commands replace the usage of ``./manage.py`` (thus it's removed). Those
correspond 1 to 1 to their ``./manage.py`` counterparts. Those commands mainly
exists so that manage.py can be deleted (less top-level files in project dir).
"""
from __future__ import absolute_import
from . import cli
