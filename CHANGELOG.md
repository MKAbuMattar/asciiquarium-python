# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

The version lives in `asciiquarium/__version__.py` and is mirrored in `pyproject.toml`.

## [Unreleased]

### Added

- **Feeding.** Press `F` to drop a flake of food below the waterline. It sinks with a slight
  sideways drift; fish within range break off and chase it, preferring flakes already ahead
  of them so a fish between two does not stall on the spot. A flake is only eaten when it
  reaches the fish's mouth rather than anywhere its bounding box overlaps. Ten flakes at
  once is the cap, so holding the key down cannot fill the tank.

  Based on [#7](https://github.com/MKAbuMattar/asciiquarium-python/pull/7) by
  [@klwill1192](https://github.com/klwill1192). Reworked before landing: pursuit is clamped
  at the waterline and the floor (an unclamped fish followed food off the bottom of the
  screen and was culled, so feeding made fish disappear), steering adjusts position for the
  frame instead of mutating the fish's stored velocity (which accumulated), and the mouth
  animation drifts at the fish's own speed rather than holding a reference to it. The
  Happy Fish and easter-egg modes from that PR are not included — see `ROADMAP.md`.

- `tests/` — the first tests in this repository, covering the feeding geometry. They need no
  terminal, because the parts that break are not the parts that need one.

- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, a pull
  request template, and issue forms for bug reports, rendering problems, and feature
  requests. The rendering-problem form exists because "it looks wrong" depends entirely on
  the terminal emulator, `$TERM`, locale, and window size — and a report without those four
  is not actionable.
- `.github/workflows/validate.yml` — lint, type-check, and build on every pull request.
  Nothing was checked automatically before this.
- `AGENTS.md` and `CLAUDE.md` — contributor and agent orientation: module layout, the
  shape/colour-mask pairing that every entity depends on, depth conventions, the
  death-callback lifecycle, and how to verify a change you cannot see in a diff.
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

[Unreleased]: https://github.com/MKAbuMattar/asciiquarium-python/compare/v2.2.0...HEAD
[2.2.0]: https://github.com/MKAbuMattar/asciiquarium-python/releases/tag/v2.2.0
