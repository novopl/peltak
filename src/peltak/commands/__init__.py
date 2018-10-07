# -*- coding: utf-8 -*-
""" Commands implementation.

Kept in a separate package to reduce the number of imports and file sizes for
the commands module. This way the commands module contain only code used by
click to generate the completion and everything else is imported when used.
"""
from __future__ import absolute_import, unicode_literals
