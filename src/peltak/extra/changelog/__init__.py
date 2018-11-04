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

Overview
========

This package adds the commands that allow you to greatly reduce the amount of
work required in maintaining a change log for your releases. The main command
**peltak changelog** will parse all commits since the last release and extract
all features/changes/fixes implemented. To achieve this, it will look for
specific tags in the commit descriptions. Once all those are found it will print
a nice change log. Here's an example::

    $ peltak changelog
    v0.21.2

    Features:
    - A description of a feature, taken from the commit message
    - Each feature has it's own list item
    - And each commit can have multiple features and/or fixes defined

    Changes:
    - One thing had to be change to something else.
    - Another thing also had to be changed.

    Fixes:
    - Description of the first fix
    - Each fix has it's own list item


Commit Format
=============

.. code-block:: text

    <title>

    <description text>

    (<tag>) <feature description>

    <description text>

Example
-------

.. code-block:: text

    Just added some new cool feature

    (feature) This feature allows the user to do many
    great things.
    (fix) This feature also fixes some issues we had
    before

    Closes #1


Configuration
=============

The command can be configured through `pelconf.yaml`. You can define what tags
are searched and what is their corresponding header in the changelog. Here is
an example:

.. code-block:: yaml

    changelog:
      tags:
        - header: 'New Features'
          tag: 'feature'
        - header: 'Changes since last release'
          tag: 'change'
        - header: 'Bug fixes'
          tag: 'fix'

The defaults correspond to the following configuration:

.. code-block:: yaml

    changelog:
      tags:
        - header: 'Features'
          tag: 'feature'
        - header: 'Changes'
          tag: 'change'
        - header: 'Fixes'
          tag: 'fix'

"""
from __future__ import absolute_import, unicode_literals
from .commands import changelog_cli
