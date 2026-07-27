"""What the CLI prints, and the version arithmetic behind the upgrade notice."""

import pytest

from asciiquarium.main import show_info
from asciiquarium.version_checker import (
    is_newer_version,
    parse_version,
    print_update_notice,
)


@pytest.mark.parametrize("key", ["Q or q", "P or p", "R or r", "F or f", "I or i"])
def test_info_screen_documents_every_control(key, capsys):
    """`--info` and the in-app overlay are written out separately and drift.

    Feeding shipped with the overlay updated and this screen left behind; this
    is the cheap half of the fix until they are built from one source.
    """
    show_info()
    assert key in capsys.readouterr().out


def test_info_screen_states_the_size_the_code_actually_enforces(capsys):
    """update_term_size raises below 40x15. The text used to promise 80x24."""
    show_info()
    out = capsys.readouterr().out
    assert "40x15" in out
    assert "Python 3.8" in out


@pytest.mark.parametrize(
    "text,expected",
    [
        ("2.3.0", (2, 3, 0)),
        ("2.10.0", (2, 10, 0)),
        ("not a version", (0, 0, 0)),
        ("", (0, 0, 0)),
    ],
)
def test_parse_version(text, expected):
    assert parse_version(text) == expected


@pytest.mark.parametrize(
    "current,latest,newer",
    [
        ("2.3.0", "2.3.1", True),
        ("2.9.0", "2.10.0", True),  # not a string comparison
        ("2.3.0", "2.3.0", False),
        ("2.4.0", "2.3.0", False),
    ],
)
def test_is_newer_version(current, latest, newer):
    assert is_newer_version(current, latest) is newer


def test_update_notice_names_both_versions(capsys):
    print_update_notice("9.9.9")
    out = capsys.readouterr().out
    assert "9.9.9" in out
    assert "NEW VERSION AVAILABLE" in out
