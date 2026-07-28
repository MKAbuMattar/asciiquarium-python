"""Frame pacing.

The loop itself needs a terminal, but the arithmetic that decides when the next
frame is due does not, and that arithmetic is the whole of the fix: before it,
pacing was a side effect of the input timeout, so a keypress bought a frame and
holding a key ran the aquarium at the keyboard's repeat rate.
"""

from asciiquarium.animation import FRAME_INTERVAL, next_deadline


def test_it_advances_by_one_interval_when_on_time():
    assert next_deadline(now=1.0, deadline=1.0, interval=0.1) == 1.1


def test_it_measures_from_the_deadline_not_from_now():
    """Otherwise every frame's draw time is added to the period and the rate
    drifts slower and slower."""
    # Frame was due at 1.0 but we only got here at 1.04.
    assert next_deadline(now=1.04, deadline=1.0, interval=0.1) == 1.1


def test_a_thousand_frames_do_not_drift():
    deadline = 0.0
    now = 0.0
    for _ in range(1000):
        now = deadline + 0.004  # consistently 4 ms late getting there
        deadline = next_deadline(now, deadline, interval=0.1)
    assert abs(deadline - 100.0) < 1e-9


def test_it_does_not_queue_catch_up_frames_after_a_stall():
    """Suspended for five seconds: the answer is the next frame, not fifty."""
    assert next_deadline(now=6.0, deadline=1.0, interval=0.1) == 6.1


def test_the_boundary_rebases_rather_than_returning_the_past():
    """Exactly one interval late is the point where advancing stops being
    ahead of now; it must not hand back a deadline that has already passed."""
    result = next_deadline(now=1.1, deadline=1.0, interval=0.1)
    assert result > 1.1


def test_the_result_is_always_in_the_future():
    for now, deadline in [(0.0, 0.0), (5.0, 1.0), (1.0, 5.0), (1.05, 1.0), (99.9, 0.0)]:
        assert next_deadline(now, deadline, interval=0.1) > now


def test_the_shipped_interval_is_ten_frames_a_second():
    """The rate the aquarium has always run at, now stated rather than implied
    by curses.halfdelay(1)."""
    assert FRAME_INTERVAL == 0.1
    assert next_deadline(0.0, 0.0) == FRAME_INTERVAL
