"""Resize handling.

The draw calls need curses; deciding what to do about a new terminal size does
not. handle_resize is the whole of the fix, so it is the part worth pinning:
before it, a resize updated two integers and left every entity placed against
the geometry it was built for.
"""

import pytest

from asciiquarium.animation import Animation


class FakeScreen:
    """The three curses calls handle_resize reaches, and nothing else."""

    def __init__(self, rows: int, cols: int):
        self.rows, self.cols = rows, cols
        self.cleared = 0

    def getmaxyx(self):
        return self.rows, self.cols

    def clear(self):
        self.cleared += 1


def make_anim(rows=24, cols=80):
    anim = Animation()
    anim.screen = FakeScreen(rows, cols)
    anim.update_term_size()
    return anim


def test_it_picks_up_the_new_size():
    anim = make_anim(24, 80)
    anim.screen.rows, anim.screen.cols = 40, 120

    anim.handle_resize(lambda _: None)

    assert anim.width() == 120
    assert anim.height() == 39  # one row reserved, as update_term_size does


def test_it_rebuilds_the_scene_rather_than_keeping_stale_entities():
    """The actual bug: waterlines stay tiled to the old width and the castle
    stays anchored to the old right edge until something rebuilds them."""
    built_at = []

    def setup(anim):
        built_at.append(anim.width())
        anim.new_entity(shape="~" * anim.width())

    anim = make_anim(24, 80)
    setup(anim)
    assert [e.size()[0] for e in anim.entities] == [80]

    anim.screen.cols = 200
    anim.handle_resize(setup)

    assert built_at == [80, 200], "setup_callback should run again at the new width"
    assert [e.size()[0] for e in anim.entities] == [200]
    assert len(anim.entities) == 1, "old entities should be gone, not appended to"


def test_it_clears_the_screen_so_the_old_scene_does_not_linger():
    anim = make_anim()
    before = anim.screen.cleared
    anim.handle_resize(lambda _: None)
    assert anim.screen.cleared == before + 1


@pytest.mark.parametrize("rows,cols", [(14, 80), (24, 39), (5, 5)])
def test_shrinking_below_the_minimum_raises(rows, cols):
    """It must not return quietly. The caller catches this to stop the loop;
    the bare `except Exception` in the input handler used to swallow it and
    leave the aquarium drawing into a screen it did not fit."""
    anim = make_anim(24, 80)
    anim.screen.rows, anim.screen.cols = rows, cols

    with pytest.raises(ValueError, match="Terminal too small"):
        anim.handle_resize(lambda _: None)


def test_a_refused_resize_does_not_half_rebuild_the_scene():
    """Raising before remove_all_entities means the scene the user can still
    see is left intact, rather than being emptied on the way out."""
    anim = make_anim(24, 80)
    anim.new_entity(shape="><>")
    anim.screen.rows = 10

    with pytest.raises(ValueError):
        anim.handle_resize(lambda _: None)

    assert len(anim.entities) == 1


def test_main_does_not_claim_sigwinch():
    """Claiming SIGWINCH here disables resize handling completely.

    ncurses installs its own SIGWINCH handler during initscr() only if the
    process has not already installed one. A handler registered before
    curses.wrapper therefore wins, and a no-op one swallows the signal: curses
    never sets its resize flag, getch() never returns KEY_RESIZE, and
    handle_resize is never reached. Measured — with the handler registered the
    aquarium ignored a resize entirely; without it, the scene rebuilds.
    """
    import inspect

    from asciiquarium.main import main

    assert "SIGWINCH" not in inspect.getsource(main)


def test_pending_error_starts_empty():
    """run() re-raises this after curses restores the terminal, so a fresh
    Animation must not look like it already failed."""
    assert Animation().pending_error is None
