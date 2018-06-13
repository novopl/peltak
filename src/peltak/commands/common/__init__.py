# -*- coding: utf-8 -*-
"""
Common code used by all commands.

All the functions are private so that fabric won't expose them as commands. This
can also be counter-acted by explicitly defining ``__all__`` but making them
private is less hassle. Just works and requires no manual management.
"""
from __future__ import absolute_import, unicode_literals
