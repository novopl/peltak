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
""" Implementation. """
from __future__ import absolute_import, unicode_literals

# stdlib imports
import re
from collections import OrderedDict
from typing import Dict, List, Optional, Pattern
import textwrap

# local imports
from peltak.core import conf
from peltak.core import git
from peltak.core import shell
from peltak.core import util
from peltak.core import versioning


@util.mark_experimental
def changelog():
    # type: () -> str
    """ Print change log since last release. """
    # Skip 'v' prefix
    versions = [x for x in git.tags() if versioning.is_valid(x[1:])]

    cmd = 'git log --format=%H'
    if versions:
        cmd += ' {}..HEAD'.format(versions[-1])

    hashes = shell.run(cmd, capture=True).stdout.strip().splitlines()
    commits = [git.CommitDetails.get(h) for h in hashes]

    tags = conf.get('changelog.tags', [
        {'header': 'Features', 'tag': 'feature'},
        {'header': 'Changes', 'tag': 'change'},
        {'header': 'Fixes', 'tag': 'fix'},
    ])

    results = OrderedDict((
        (x['header'], []) for x in tags
    ))

    for commit in commits:
        commit_items = extract_changelog_items(commit.desc, tags)
        for header, items in commit_items.items():
            results[header] += items

    lines = [
        '<35>v{}<0>'.format(versioning.current()),
        '',
    ]
    for header, items in results.items():
        if items:
            lines += [
                '',
                '<32>{}<0>'.format(header),
                '<32>{}<0>'.format('-' * len(header)),
                '',
            ]
            for item_text in items:
                item_lines = textwrap.wrap(item_text, 77)
                lines += ['- {}'.format('\n  '.join(item_lines))]

            lines += ['']

    return '\n'.join(lines)


def extract_changelog_items(text, tags):
    # type: (str) -> Dict[str, List[str]]
    """ Extract all tagged items from text.

    Args:
        text (str):
            Text to extract the tagged items from. Each tagged item is a
            paragraph that starts with a tag. It can also be a text list item.

    Returns:
        tuple[list[str], list[str], list[str]]:
            A tuple of `(features, changes, fixes)` extracted from the given
            text.

    The tagged items are usually features/changes/fixes but it can be configured
    through `pelconf.yaml`.
    """

    patterns = {x['header']: tag_re(x['tag']) for x in tags}
    items = {x['header']: [] for x in tags}
    curr_tag = None
    curr_text = ''

    for line in text.splitlines():
        if not line.strip():
            if curr_tag is not None:
                items[curr_tag].append(curr_text)
                curr_text = ''
            curr_tag = None

        for tag in tags:
            m = patterns[tag['header']].match(line)
            if m:
                if curr_tag is not None:
                    items[curr_tag].append(curr_text)
                    curr_text = ''

                curr_tag = tag['header']
                line = m.group('text')
                break

        if curr_tag is not None:
            curr_text = '{} {}'.format(curr_text.strip(), line.strip()).strip()

    if curr_tag is not None:
        items[curr_tag].append(curr_text)

    return items


def tag_re(tag):
    # type: (str) -> Pattern
    """ Return a regular expression to match tagged lines.
    Args:
        tag (str):
            A tag for which you need the regex pattern. This should be a single
            word.

    Returns:
        Pattern: Regex patter object as returned by `re.compile`.

    The returned pattern will match only the starting line that contains the
    tag. The item definition might span across multiple lines and this has to
    be handled separately
    """
    return re.compile(
        # r'\(feature\) (?P<text>.*?\n\n)',
        r'(- |\* |\s+)?\({tag}\) (?P<text>.*)'.format(tag=tag),
    )


# Used in type hint comments only (until we drop python2 support)
del Dict, List, Optional, Pattern
