# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring
from __future__ import absolute_import, unicode_literals

# local imports
from peltak import testing
from peltak.core.templates.filters import header


@testing.patch_is_tty(True)
def test_prints_in_colors_when_in_tty():
    assert header('hello') == (
        'echo "\x1b[32m= \x1b[35mhello \x1b[32m========================================================================\x1b[0m"'  # noqa
    )


@testing.patch_is_tty(False)
def test_prints_without_colors_when_not_in_tty():
    assert header('hello') == (
        'echo "= hello ========================================================================"'  # noqa
    )


@testing.patch_is_tty(False)
def test_works_with_numbers():
    assert header(123) == (
        'echo "= 123 =========================================================================="'  # noqa
    )


@testing.patch_is_tty(False)
def test_header_is_always_the_same_length():
    HDR_LEN = 80 + len('echo ""')

    assert len(header('hello')) == HDR_LEN
    assert len(header('one')) == HDR_LEN
    assert len(header('very long title')) == HDR_LEN
    assert len(header('And this is an even longer title')) == HDR_LEN
    assert len(header('aaaaa ' * 100)) == HDR_LEN
