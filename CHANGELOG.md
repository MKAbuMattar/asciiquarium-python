# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

The version lives in `asciiquarium/__version__.py` and is mirrored in `pyproject.toml`.

## [Unreleased]

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

[Unreleased]: https://github.com/MKAbuMattar/asciiquarium-python/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.3.0
[2.2.0]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.2.0
