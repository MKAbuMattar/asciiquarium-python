# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

The version lives in `asciiquarium/__version__.py` and is mirrored in `pyproject.toml`.

## [Unreleased]

## [2.4.1] - 2026-07-30

### Fixed

- **Resizing the terminal did nothing at all.** Not "handled badly" — ignored. `main()`
  registered a handler for `SIGWINCH` that did nothing with it, and ncurses only installs its
  own handler if the process has not already claimed one. So curses never learned the terminal
  had changed, `getch()` never reported `KEY_RESIZE`, and the branch meant to deal with it was
  unreachable. Removing that handler is the fix; measured with the handler in place a resize
  produced no reaction whatsoever, and without it the scene rebuilds.

  With the signal arriving, resize now rebuilds the scene instead of only updating two
  numbers. Every entity is placed against the geometry it was created in: the waterlines are
  tiled to a width, the castle is anchored to the right edge, the seaweed sits on the floor.
  Widening the window used to leave a short waterline and a castle stranded mid-screen until
  something forced a rebuild. Verified in a pty: growing 80×24 to 200×50 re-tiles the
  waterline from 80 to 200 columns.

  Shrinking below the 40×15 minimum now says so and exits, instead of being swallowed by the
  input handler's catch-all and leaving the aquarium drawing into a screen it does not fit.
  The message waits until curses has given the terminal back, so it is readable.

## [2.4.0] - 2026-07-28

### Fixed

- **Holding a key no longer speeds the aquarium up.** There was no frame clock. Pacing was a
  side effect of the 100 ms input timeout, and a keypress returns from that timeout early, so
  every early return drew a frame: at a normal keyboard repeat rate the animation ran close to
  five times too fast. Measured at 9.9 frames a second idle and 47.7 under key repeat before
  the change; 9.9 and 10.0 after. Frames are now scheduled against a monotonic deadline, and
  the input timeout does nothing but wait for input.

  The deadline advances by whole intervals rather than from the current time, so drawing time
  does not accumulate into the period and the rate stays put over a long run. If the process
  is starved for longer than one interval, it drops the frames it missed instead of queueing a
  burst to catch up, which is what would otherwise make the aquarium lurch after the terminal
  was suspended or resized. The rate itself is unchanged at ten frames a second, but it is now
  named (`FRAME_INTERVAL`) rather than implied by `curses.halfdelay(1)`.

## [2.3.1] - 2026-07-27

### Fixed

- **The upgrade notice no longer lands on top of the aquarium.** The PyPI poll ran on a
  background thread that printed a twenty-line box straight into the curses screen if the
  answer arrived in time. Curses never knew it happened, so nothing could repaint over it.
  The poll is silent now and the notice prints once the animation has given the terminal
  back.
- **Multi-frame creatures are measured across all of their frames.** `Entity.size()` reported
  frame 0's dimensions, and it feeds both collision detection and the offscreen cull — so the
  whale, the sea monsters and the ducks were being culled and collided against a box smaller
  than the one they are drawn in.
- The lead dolphin asked for `"blue"`; colour names are uppercase, so it swam past uncoloured.
- `--info` claimed Python 3.7 and an 80×24 minimum (the code enforces 3.8 and 40×15) and did
  not mention the feeding key, which shipped in 2.3.0.
- `asciiquarium/__init__.py` assigned `__all__` twice, and the second assignment dropped every
  version symbol the first one exported. It also rebound `main` to the *function*, so
  `import asciiquarium.main` handed back the function instead of the module. The convenience
  import is gone; `import asciiquarium` no longer pulls in curses as a side effect.
- **The release pipeline could fail a release that had actually succeeded.** Its post-upload
  check polled `info.version` on PyPI's project endpoint, which is CDN-cached and lags: after
  2.3.0 was published that document kept reporting 2.2.0 for minutes while the release was
  already installable. It now asks the per-version URL, which answers immediately, and a
  transient 5xx is retried instead of aborting the release. `tests/test_release_version.py`
  covers both directions, since a false negative fails a good release and a false positive
  would tag one that never uploaded.
- README: three emoji had been corrupted into replacement characters, the troubleshooting
  section contradicted the requirements section on the minimum terminal size, "30 FPS" was
  never true (pacing comes from the 100 ms input timeout), the fish count was out of date, and
  the project tree and development commands had drifted from the repository.

### Added

- `py.typed`, so the annotations are visible to anything installing this package.
- The CI import sweep covers Python 3.14, which the classifiers had claimed without ever being
  tested. Windows and macOS stay out of CI on purpose — those runners bill at 2x and 10x
  against a free-tier budget.
- `tests/test_art.py` covers the invariants that fail silently — every fish design pairing its
  shape frames with mask frames, masks covering every row, no placeholder digit surviving
  `rand_color`, and every spawned entity naming a colour the renderer actually knows.
  `tests/test_cli.py` covers the version arithmetic, the upgrade notice, and the `--info`
  text, so the feeding key cannot quietly fall out of it again.
- `.github/dependabot.yml` for the actions, and a `CODEOWNERS` file — `main` was set to
  require code-owner review with no code owners defined, which matched nobody.

### Changed

- `special.py` imports `rand_color` instead of inlining the same twelve-colour loop twice.
- The dead "Question / usage help" contact link is gone; it pointed at Discussions, which is
  disabled on this repository.

## [2.3.0] - 2026-07-27

### Added

**Feeding.** Press `F` to drop a flake of food below the waterline. It sinks with a slight
sideways drift. Fish within range break off and chase it, preferring flakes already ahead of
them, so a fish caught between two keeps swimming instead of stalling. A flake is eaten only
when it reaches the fish's mouth, not merely when it overlaps the bounding box. Ten flakes at
once is the cap, so holding the key down cannot fill the tank.

Based on [#7](https://github.com/MKAbuMattar/asciiquarium-python/pull/7) by
[@klwill1192](https://github.com/klwill1192), reworked before landing. Pursuit is now clamped
at the waterline and the floor, because an unclamped fish followed food off the bottom of the
screen and was culled, which meant feeding your fish made them disappear. Steering adjusts
position for the frame rather than mutating the fish's stored velocity, which used to
accumulate. Direction is read through a helper that copes with a hooked fish, whose
`callback_args` is a dict rather than a list. The mouth animation drifts at the fish's own
speed instead of holding a reference to it. Happy Fish and the easter-egg mode from that pull
request are not included; see `ROADMAP.md` item 24.

### Added for contributors

- `tests/` holds the first tests in this repository, covering the feeding geometry. They need
  no terminal, because the parts that break are not the parts that need one.
- `.github/workflows/validate.yml` runs lint, type-checking, tests, an import sweep across
  every supported Python version, a build, and a check that `__version__.py` and
  `pyproject.toml` agree. Nothing was checked automatically before this.
- `.github/workflows/release.yml` plus `scripts/release_version.py` publish to PyPI from a
  `release/<version>` branch with a labelled pull request. Preparing is repeatable and
  reversible; merging is the one irreversible step.
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, a pull
  request template, and issue forms. Bug reports and rendering problems are separate forms
  because they need different evidence: "it looks wrong" is unactionable without the terminal
  emulator, `$TERM`, size, and locale, so that form asks for all four.
- `AGENTS.md` and `CLAUDE.md` cover the module layout, the shape and colour-mask pairing every
  entity depends on, the depth conventions, the death-callback lifecycle, and how to verify a
  change you cannot see in a diff.
- This changelog and `ROADMAP.md`.

## [2.2.0]

### Added

- Info overlay, toggled with `i` while the aquarium is running and dismissed with `i` or
  `Esc`. Pauses the animation while open.

### Changed

- Type hints and error handling across the animation and entity modules.
- Ruff and mypy target Python 3.8.

### Removed

- The farewell message printed on exit.

## Earlier releases

Releases before 2.2.0 predate this changelog. See the
[commit history](https://github.com/MKAbuMattar/asciiquarium-python/commits/main) and the
[releases page](https://github.com/MKAbuMattar/asciiquarium-python/releases).

[Unreleased]: https://github.com/MKAbuMattar/asciiquarium-python/compare/v2.4.1...HEAD
[2.4.1]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.4.1
[2.4.0]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.4.0
[2.3.1]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.3.1
[2.3.0]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.3.0
[2.2.0]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.2.0
