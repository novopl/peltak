# Copyright 2017-2021 Mateusz Klos
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

from peltak.core import conf, git, shell, versioning

from .types import ChangelogItems, ChangelogTag


DEFAULT_TAGS = (
    {"tag": "feature", "header": "Features"},
    {"tag": "change", "header": "Changes"},
    {"tag": "fix", "header": "Fixes"},
)
DEFAULT_TAG_FORMAT = '({tag})'
DEFAULT_CONTINUATION_TAG = '_more'


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
    commits = _get_commits_in_range(start_rev, end_rev)
    tags = [ChangelogTag(**x) for x in conf.get("changelog.tags", DEFAULT_TAGS)]
    results: ChangelogItems = OrderedDict((tag.header, []) for tag in tags)

    for commit in commits:
        full_message = f"{commit.title}\n\n{commit.desc}"
        commit_items = extract_changelog_items(full_message, tags)
        for header, items in commit_items.items():
            results[header] += items

    return results


def _get_commits_in_range(
    start_rev: Optional[str],
    end_rev: Optional[str]
) -> List[git.CommitDetails]:
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

    hashes = shell.run(cmd, capture=True).stdout.strip().splitlines()
    return [git.CommitDetails.get(h) for h in hashes]


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
                # Newlines are only inserted via continuation tags, all other
                # newlines are removed during changelog items extraction.
                blocks = item_text.splitlines()
                item_content = '\n'.join(
                    '\n'.join(textwrap.wrap(b, width=77)) for b in blocks
                )
                item_content = textwrap.indent(item_content, prefix='  ')
                item_lines = item_content.splitlines()
                lines.append(f"- <1>{item_lines[0].lstrip()}<0>")
                lines += item_lines[1:]

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
    through ``pelconf.yaml``.
    """
    tag_format = conf.get("changelog.tag_format", DEFAULT_TAG_FORMAT)
    continuation_tag = conf.get("changelog.continuation_tag", DEFAULT_CONTINUATION_TAG)
    patterns = {
        tag.header: tag_re(tag_format.format(tag=tag.tag))
        for tag in tags
    }
    more_pttrn = tag_re(tag_format.format(tag=continuation_tag))
    items: ChangelogItems = {tag.header: [] for tag in tags}
    curr_tag = None
    curr_text = ''
    last_tag = None

    for line in text.splitlines():
        if not line.strip():
            if curr_tag is not None:
                items[curr_tag].append(curr_text)
                curr_text = ''
            last_tag = curr_tag
            curr_tag = None

        more_match = more_pttrn.match(line)

        if more_match and last_tag:
            # If it's a continuation tag, then just add it's text to the last
            # used tag. This only works if there was a previous tag.
            curr_tag = last_tag
            curr_text = items[last_tag][-1]
            items[last_tag] = items[last_tag][:-1]
            line = more_match.group('text')
        else:
            for tag in tags:
                m = patterns[tag.header].match(line)
                if m:
                    if curr_tag is not None:
                        # If we're already in a tag definition and we encountered
                        # a beginning of a new tag, just finish by adding new
                        # item to the current tag item list.
                        items[curr_tag].append(curr_text)
                        curr_text = ''
                    curr_tag = tag.header
                    line = m.group('text')
                    break

        if curr_tag is not None:
            if more_match:
                curr_text = '{}\n{}'.format(curr_text, line.strip()).strip()
            else:
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
