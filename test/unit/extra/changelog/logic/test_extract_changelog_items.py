# pylint: disable=missing-docstring
import pytest

from peltak import testing
from peltak.extra.changelog import logic
from peltak.extra.changelog.types import ChangelogTag


@pytest.mark.parametrize('header,tag', [
    ('Features', 'feature'),
    ('Changes', 'change'),
    ('Fixes', 'fix'),
])
@testing.patch_pelconf({})
def test_detects_each_tag(header, tag):
    desc = '\n'.join([
        '({tag}) This is my item'.format(tag=tag),
        'and it has multiple lines',
    ])

    items = logic.extract_changelog_items(desc, tags=[
        ChangelogTag(header='Features', tag='feature'),
        ChangelogTag(header='Changes', tag='change'),
        ChangelogTag(header='Fixes', tag='fix'),
    ])

    assert len(items[header]) == 1
    assert items[header][0] == 'This is my item and it has multiple lines'


@pytest.mark.parametrize('header,tag', [
    ('Features', 'feature'),
    ('Changes', 'change'),
    ('Fixes', 'fix'),
])
@testing.patch_pelconf({})
def test_supports_dense_descriptions(header, tag):
    desc = '\n'.join([
        '({tag}) This is my item'.format(tag=tag),
        'and it has multiple lines',
        '({tag}) This is my second item'.format(tag=tag),
    ])

    items = logic.extract_changelog_items(desc, tags=[
        ChangelogTag(header='Features', tag='feature'),
        ChangelogTag(header='Changes', tag='change'),
        ChangelogTag(header='Fixes', tag='fix'),
    ])

    assert len(items[header]) == 2
    assert items[header][0] == 'This is my item and it has multiple lines'
    assert items[header][1] == 'This is my second item'


@pytest.mark.parametrize('header,tag', [
    ('Features', 'feature'),
    ('Changes', 'change'),
    ('Fixes', 'fix'),
])
@testing.patch_pelconf({})
def test_supports_loose_descriptions(header, tag):
    desc = '\n'.join([
        '',
        '({tag}) This is my item'.format(tag=tag),
        'and it has multiple lines',
        '',
        '({tag}) This is my second item'.format(tag=tag),
    ])

    items = logic.extract_changelog_items(desc, tags=[
        ChangelogTag(header='Features', tag='feature'),
        ChangelogTag(header='Changes', tag='change'),
        ChangelogTag(header='Fixes', tag='fix'),
    ])

    assert len(items[header]) == 2
    assert items[header][0] == 'This is my item and it has multiple lines'
    assert items[header][1] == 'This is my second item'


@testing.patch_pelconf({})
def test_supports_all_tags_used_together():
    desc = '\n'.join([
        '(fix) This is my fix',
        'and it has multiple lines',
        '',
        '(change) This is my change',
        '(feature) This is my feature',
    ])

    items = logic.extract_changelog_items(desc, tags=[
        ChangelogTag(header='Features', tag='feature'),
        ChangelogTag(header='Changes', tag='change'),
        ChangelogTag(header='Fixes', tag='fix'),
    ])

    assert len(items['Features']) == 1
    assert items['Features'][0] == 'This is my feature'

    assert len(items['Changes']) == 1
    assert items['Changes'][0] == 'This is my change'

    assert len(items['Fixes']) == 1
    assert items['Fixes'][0] == 'This is my fix and it has multiple lines'


@testing.patch_pelconf({})
def test_ignores_non_tagged_text():
    desc = '\n'.join([
        'This is some text that should be gnored',
        '(feature) This is my feature',
        '',
        'This also should be ignored'
    ])

    items = logic.extract_changelog_items(desc, tags=[
        ChangelogTag(header='Features', tag='feature'),
    ])

    assert len(items['Features']) == 1
    assert items['Features'][0] == 'This is my feature'


@testing.patch_pelconf({})
def test_support_continuation_tags():
    desc = '\n'.join([
        '(feature) This is my item',
        '',
        '(_more) and it has a continuation tag.',
    ])

    items = logic.extract_changelog_items(desc, tags=[
        ChangelogTag(header='Features', tag='feature'),
    ])

    assert len(items['Features']) == 1
    assert items['Features'][0] == 'This is my item\nand it has a continuation tag.'
