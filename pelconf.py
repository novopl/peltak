# -*- coding: utf-8 -*-
""" peltak configuration file.

See `peltak <https://github.com/novopl/peltak>`_ for more information.
"""
from __future__ import absolute_import

# This is just so in this repo we use the most current version of the source
# for peltak, not the installed one.
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, join(abspath(dirname(__file__)), 'src'))
