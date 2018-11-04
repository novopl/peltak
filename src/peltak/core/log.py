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
Helpers for nice shell output formatting.
"""
from __future__ import absolute_import, unicode_literals

# stdlib imports
from typing import Any

# local imports
from . import shell


def info(msg, *args, **kw):
    # type: (str, *Any, **Any) -> None
    """ Print sys message to stdout.

    System messages should inform about the flow of the script. This should
    be a major milestones during the build.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <32>{}<0>'.format(msg))


def err(msg, *args, **kw):
    # type: (str, *Any, **Any) -> None
    """ Per step status messages

    Use this locally in a command definition to highlight more important
    information.
    """
    if len(args) or len(kw):
        msg = msg.format(*args, **kw)

    shell.cprint('-- <31>{}<0>'.format(msg))


# Used in docstrings only until we drop python2 support
del Any
