# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

The version lives in `asciiquarium/__version__.py` and is mirrored in `pyproject.toml`.

## [Unreleased]

### Added

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
