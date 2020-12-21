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
""" Implementation. """

import re
import textwrap
from collections import OrderedDict
from typing import Dict, List, Pattern

from peltak.core import conf
from peltak.core import git
from peltak.core import shell
from peltak.core import util
from peltak.core import versioning
from .types import ChangelogItems, ChangelogTag


@util.mark_experimental
def changelog() -> str:
    """ Print change log since last release.

    TODO: Add the ability to omit sections of changelog in the output. This way
        We can use changelog command to automatically generate changelog for
        public releases without any references to the ticket board but still
        have the ability to associate tickets with releases. For example we can
        add a (jira) tag that would be used to pass the JIRA ticket URL and then
        in the official changelog we just omit the jira section. We can still
        use the jira section in developer tooling like PRs and internal
        progress tracking.
    TODO: Add ability to specify the starting point for the changelog command.
        Ideally the user could specify the base branch and get the changelog
        only for his branch. This would make it very easy to use tags in the
        commit messages in your branch and then use peltak changelog to generate
        a PR description.
    """
    # Skip 'v' prefix
    versions = [x for x in git.tags() if versioning.is_valid(x[1:])]

    cmd = 'git log --format=%H'
    if versions:
        cmd += ' {}..HEAD'.format(versions[-1])

    hashes = shell.run(cmd, capture=True).stdout.strip().splitlines()
    commits = [git.CommitDetails.get(h) for h in hashes]

    tags = [
        ChangelogTag(**x) for x in
        conf.get('changelog.tags', (
            {'header': 'Features', 'tag': 'feature'},
            {'header': 'Changes', 'tag': 'change'},
            {'header': 'Fixes', 'tag': 'fix'},
        ))
    ]

    results: ChangelogItems = OrderedDict((tag.header, []) for tag in tags)

    for commit in commits:
        commit_items = extract_changelog_items(commit.desc, tags)
        for header, items in commit_items.items():
            results[header] += items

    version = versioning.current()
    lines = [
        '<35>v{}<0>'.format(version),
        '<32>{}<0>'.format('=' * (len(version) + 1)),
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


def extract_changelog_items(text: str, tags: List[ChangelogTag]) -> Dict[str, List[str]]:
    """ Extract all tagged items from text.

    Args:
        text (str):
            Text to extract the tagged items from. Each tagged item is a
            paragraph that starts with a tag. It can also be a text list item.

    Returns:
        tuple[list[str], list[str], list[str]]:
            A tuple of ``(features, changes, fixes)`` extracted from the given
            text.

    The tagged items are usually features/changes/fixes but it can be configured
    through `pelconf.yaml`.
    """

    patterns = {tag.header: tag_re(tag.tag) for tag in tags}
    items: ChangelogItems = {tag.header: [] for tag in tags}
    curr_tag = None
    curr_text = ''

    for line in text.splitlines():
        if not line.strip():
            if curr_tag is not None:
                items[curr_tag].append(curr_text)
                curr_text = ''
            curr_tag = None

        for tag in tags:
            m = patterns[tag.header].match(line)
            if m:
                if curr_tag is not None:
                    items[curr_tag].append(curr_text)
                    curr_text = ''

                curr_tag = tag.header
                line = m.group('text')
                break

        if curr_tag is not None:
            curr_text = '{} {}'.format(curr_text.strip(), line.strip()).strip()

    if curr_tag is not None:
        items[curr_tag].append(curr_text)

    return items


def tag_re(tag: str) -> Pattern:
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
