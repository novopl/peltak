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
from typing import Dict, List, Optional, Pattern

from peltak.core import conf
from peltak.core import git
from peltak.core import shell
from peltak.core import util
from peltak.core import versioning
from .types import ChangelogItems, ChangelogTag


DEFAULT_TAGS = (
    {"tag": "feature", "header": "Features"},
    {"tag": "change", "header": "Changes"},
    {"tag": "fix", "header": "Fixes"},
)
DEFAULT_TAG_FORMAT = '({tag})'


@util.mark_experimental
def changelog(
    start_rev: Optional[str] = None,
    end_rev: Optional[str] = None,
    title: Optional[str] = None,
) -> str:
    """ Print changelog for given git revision range. """
    # Skip 'v' prefix
    changelog_items = _get_all_changelog_items(start_rev, end_rev)
    return _render_changelog(title, changelog_items)


def _get_all_changelog_items(
    start_rev: Optional[str],
    end_rev: Optional[str]
) -> ChangelogItems:
    hashes = _get_commits_in_range(start_rev, end_rev)
    commits = [git.CommitDetails.get(h) for h in hashes]
    tags = [ChangelogTag(**x) for x in conf.get("changelog.tags", DEFAULT_TAGS)]
    results: ChangelogItems = OrderedDict((tag.header, []) for tag in tags)

    for commit in commits:
        commit_items = extract_changelog_items(commit.desc, tags)
        for header, items in commit_items.items():
            results[header] += items

    return results


def _get_commits_in_range(start_rev: Optional[str], end_rev: Optional[str]) -> List[str]:
    if not start_rev:
        versions = [x for x in git.tags() if versioning.is_valid(x[1:])]
        start_rev = versions[-1] if versions else ''

    if not end_rev:
        end_rev = 'HEAD'

    cmd = 'git log --format=%H'
    if start_rev and end_rev:
        cmd += f" {start_rev}..{end_rev}"
    elif end_rev:
        cmd += f" {end_rev}"

    return shell.run(cmd, capture=True).stdout.strip().splitlines()


def _render_changelog(title: Optional[str], changelog_items: ChangelogItems) -> str:
    if title is None:
        # title is None if title parameter wasn't pass. To show empty title
        # you can use --title ''
        title = f"v{versioning.current()}"

    lines = []
    if title:
        lines += [
            f"<35>{title}<0>",
            f"<32>{'=' * (len(title) + 1)}<0>",
            "",
        ]

    for header, items in changelog_items.items():
        if items:
            lines += [
                "",
                f"<32>{header}<0>",
                f"<32>{'-' * len(header)}<0>",
                "",
            ]
            for item_text in items:
                item_lines = textwrap.wrap(item_text, 77)
                lines += ["- {}".format('\n  '.join(item_lines))]

            lines += [""]

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
    tag_format = conf.get("changelog.tag_format", DEFAULT_TAG_FORMAT)
    patterns = {
        tag.header: tag_re(tag_format.format(tag=tag.tag))
        for tag in tags
    }
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
        r'(- |\* |\s+)?{tag} (?P<text>.*)'.format(tag=re.escape(tag)),
    )
