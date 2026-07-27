# Roadmap

Paced improvements to the port. Each increment lands as its own conventional commit, must
keep `uvx ruff check asciiquarium` and `uvx mypy --ignore-missing-imports asciiquarium` at
zero findings, and gets a `CHANGELOG.md` entry.

Scope is the package, the tooling that checks it, and the docs. Ordered by what an audit of
the current tree actually exposed, not by what would be nice to have. Everything in phase 1
is a defect a user can hit today; every item names the evidence rather than the aspiration.

## Phase 1 — Defects

| # | Increment | Status |
|---|---|---|
| 1 | **The update check can corrupt the screen.** `main()` starts `check_for_updates` on a daemon thread and then hands the terminal to curses. If PyPI answers within its 2-second timeout and a newer version exists, the thread prints a 20-line box straight into the curses screen. Nothing can repaint over it because curses does not know it happened. | ✅ done — the poll now runs `silent=True` and stashes its answer; `print_update_notice()` runs after `curses.wrapper` returns |
| 2 | **Frame rate is whatever the keyboard says it is.** There is no frame clock: pacing comes from `curses.halfdelay(1)` blocking for 100ms in `getch()`. A keypress returns immediately, so holding any key runs the aquarium at keyboard-repeat speed. Drive the loop from a monotonic deadline and keep `halfdelay` only for input. | planned |
| 3 | **Multi-frame entities report the wrong size.** `Entity._update_dimensions` measures `shapes[0]` only, but `size()` feeds both collision detection and the `die_offscreen` test. The whale, the sea monsters, and the ducks all have frames of differing widths, so they are culled and collide against a stale box. | ✅ done — measured across every frame, with a regression test |
| 4 | **Resize leaves the scene stale.** `KEY_RESIZE` updates `screen_width`/`screen_height` and nothing else. Waterlines stay tiled to the old width, the castle stays anchored to the old right edge, and `update_term_size`'s too-small `ValueError` is swallowed by the bare `except Exception` in the input handler. Rebuild the scene on resize — the `r` key already does exactly this. | planned |
| 5 | **Two one-token bugs.** `special.py` sets `default_color="blue"` lowercase on the lead dolphin; `color_pairs` is keyed uppercase, so it renders uncoloured. `asciiquarium/__init__.py` assigns `__all__` twice, and the second assignment silently drops every version symbol the first one exported. | ✅ done — both fixed; a test now asserts every spawned entity's `default_color` is a real colour name |
| 6 | **`__init__.py` shadows its own submodule.** `from .main import main` rebinds the name `main` on the package, so `import asciiquarium.main as m` hands back the *function*, not the module, and `python -m asciiquarium.main` warns about it. The console script still resolves, which is why nobody has noticed. | ✅ done — convenience import dropped; `import asciiquarium` no longer pulls in curses either |

## Phase 2 — Nothing verifies any of this

| # | Increment | Status |
|---|---|---|
| 7 | **CI.** `.github/workflows/validate.yml` runs `ruff`, `mypy`, an import sweep and CLI smoke check across every supported Python version, a build, and a check that `__version__.py` and `pyproject.toml` agree. Both linters report zero findings on `main`, so the gate is meaningful from day one: anything red was introduced by the change under review. Nothing had ever been checked automatically before. | ✅ done |
| 8 | **A smoke test.** `pytest` was a declared dev dependency with zero test files. `tests/test_feeding.py` broke the seal — the feeding geometry, no terminal required — and CI runs it. `tests/test_art.py` adds the art invariants (frame/mask pairing, mask row coverage, no stray placeholder digits, every `default_color` a real colour) and `Entity` sizing across frames; `tests/test_cli.py` covers `parse_version`/`is_newer_version`, the update notice, and the `--info` text. Still uncovered: `Entity.should_die`, and the in-app overlay, whose text is built inside a curses call and cannot be reached without one — see (13). | in progress |

## Phase 3 — Consolidation

| # | Increment | Status |
|---|---|---|
| 9 | **One formatter, one linter.** `black`, `isort`, and `ruff` are all configured, and `ruff` already does both other jobs (`"I"` is in the selected rule set). The two configs disagree: `isort` sets `line_length = 88`, `ruff` sets `line-length = 100`. Collapse onto `ruff format` + `ruff check --fix`. Note that `ruff format --check` currently *fails* on `main` — the tree is black-formatted at a different width, so this lands as one reformat commit and only then becomes a CI gate. | planned |
| 10 | **One dev-dependency list.** Dev deps are declared three times — `[project.optional-dependencies].dev`, `[tool.hatch.envs.default]`, and an empty `[dependency-groups].dev` — with conflicting bounds (`mypy>=1.0.0` in one, `mypy<1.5.0` in the other). Keep one. | planned |
| 11 | **`[tool.mypy] python_version = "3.8"` is rejected by current mypy.** Every run prints `Python 3.8 is not supported (must be 3.10 or higher)` before doing anything. It still exits 0, so it looks fine and is easy to miss — but the version the config asks for is not the version being checked. Blocked on (19). | planned |
| 12 | **Deduplicate the colour randomiser.** `rand_color()` exists in `fish.py`; `special.py` inlines the identical twelve-colour loop twice for the two big fish. | ✅ done — `special.py` imports it |
| 13 | **Deduplicate the info screen.** The feature list, controls, and credits are written out twice: `main.show_info()` for `--info` and `Animation.show_info_overlay()` for the `i` key. The stale facts in the `--info` copy are fixed and `tests/test_cli.py` now pins them, but the duplication itself is untouched — the overlay is still the half no test can reach, and the drift will recur. Build both from one source. | in progress |
| 14 | **Name the waterline constant.** `WATER_LINE_BOTTOM` now exists in `animation.py` and the feeding code uses it, but `9` is still spelled literally in `fish.py` (a local `water_line_bottom`, and `height() - 9`), `environment.py`, and three times in `special.py`. Finish the job. | in progress |
| 15 | **Break the import cycle.** `entities/*` imports `DEPTH` from `animation`, so `animation` cannot import `entities` at module level. Anything needing to spawn an entity from the animation layer has to do a function-local import. Move `DEPTH` (and the waterline constant from 14) into their own module that both sides import. | planned |
| 16 | **Delete what is already dead.** `MANIFEST.in` (hatchling ignores it), the `SIGWINCH` handler in `main()` (ncurses installs its own during `initscr`, after this one, so it never fires), the `callback_args == "hooked"` string branch in `fishhook_cb`, the unused `position()` call in `retract()`, and the `elif showing_info: pass` no-op in the run loop. | planned |

## Phase 4 — Quality

| # | Increment | Status |
|---|---|---|
| 17 | **The renderer draws one character at a time.** `_draw_entity` calls `addch` per cell with a per-cell colour lookup and three `try` frames. At 200×50 that is up to 10,000 calls per frame. Batching each run of same-coloured characters into one `addstr` is the same output with an order of magnitude fewer calls, and it is what makes a higher frame rate affordable once (2) lands. | planned |
| 18 | **The info overlay does not fit its own minimum terminal.** Its box is 73 columns of hardcoded rule and it runs ~35 lines, but the enforced minimum is 40×15. Below ~75 columns every line is truncated mid-box; below ~35 rows the bottom is cut off, including "press I or ESC to return". Reflow to the available width, or state a real minimum for the overlay and show a short form under it. | planned |
| 19 | **Drop Python 3.8.** It is past end-of-life, it is what pins `typing.List`/`Dict` throughout, and `windows-curses` is already special-cased around version boundaries. Moving to 3.9+ costs nothing, removes a column from the CI matrix, and unblocks (11). | planned |
| 20 | **Ship `py.typed`.** The package is annotated and `mypy` is configured, but without the marker no downstream consumer sees any of it. | ✅ done — `asciiquarium/py.typed` |
| 21 | **Colour is the only channel.** Creatures are distinguished purely by hue, and `init_pair` failures are swallowed, so a 8-colour or monochrome terminal degrades silently rather than falling back deliberately. Nothing here encodes meaning yet, so this is not urgent — but it is worth settling before anything does. | planned |
| 22 | **Release workflow.** `.github/workflows/release.yml`. Branch as `release/<version>`, open a pull request to `main`, add the `release` label. Preparing (bump, changelog, gate, build, wheel smoke test) happens while the PR is open and is idempotent; **merging** is the single irreversible act that uploads to PyPI, tags, and writes the Release page. Split that way because PyPI forbids re-uploading a version, so the point of no return should be one deliberate click and the PR diff should show exactly what ships. Authenticates with the `PYPI_API_TOKEN` secret on the `pypi` environment. | ✅ done |
| 25 | **Move the release to trusted publishing.** The token is a long-lived credential that has to be rotated by hand. PyPI's OIDC publisher removes it entirely — configure a GitHub publisher on the project, then drop the `TWINE_*` env block for `pypa/gh-action-pypi-publish`. Not urgent, but it is strictly better once someone does the one-time PyPI-side setup. | planned |

## Phase 5 — Found by the July 2026 audit

| # | Increment | Status |
|---|---|---|
| 26 | **Emoji in CLI output crashes on a non-UTF-8 Windows console.** `show_info()`, the `argparse` description and epilog, and several error messages contain emoji. On Windows, a redirected or piped stdout falls back to the legacy code page, and printing 🐠 raises `UnicodeEncodeError` — so `asciiquarium --info > file` and `asciiquarium --help \| more` can die on a supported platform. This is why the new cross-platform CI job runs only `--version`. Either force UTF-8 on stdout at startup or keep the decorative characters out of anything that must survive a pipe. | planned |
| 27 | **Nothing gates the merge that publishes.** `main` is protected, but with zero required approvals, no required status checks, and `require_code_owner_reviews` on with no `CODEOWNERS` file to match (that file now exists). `validate.yml` is not a required check, so a pull request whose CI is red can still be merged — and merging a `release/*` PR uploads to PyPI, which cannot be undone. Require `lint`, `import`, `build`, and the release job's `prepare` before merge. Repository setting, not a file in the tree. | planned |
| 28 | **Windows and macOS are never built or run in CI.** Three platforms are advertised as fully supported and only one is ever exercised. Deliberately *not* fixed with CI jobs: Windows runners bill at 2x and macOS at 10x against a free-tier minute budget, which is not a trade worth making for a screensaver. The real content of this item is a support claim that cannot be verified — and one that is wrong: the `windows-curses` marker is `python_version < '3.13'`, so on Windows 3.13+ nothing provides curses and the app raises at import, while the classifiers claim 3.13 and 3.14. Either find a curses provider for modern Windows or stop claiming those versions there. | needs a decision, not CI |
| 29 | **Python 3.14 was claimed and never tested.** The classifier and the README both promised it; the CI matrix stopped at 3.13. Added. | ✅ done |
| 30 | **The update poll cannot be turned off.** Every launch makes an outbound HTTPS request to pypi.org. `SECURITY.md` names that path as the largest piece of this package's attack surface, and there is no flag or environment variable to skip it — an offline, air-gapped, or privacy-minded user has no way to say no. `--no-update-check` plus an environment variable, defaulting to on. | planned |
| 31 | **Five fish mask rows are shorter than their shape rows.** In `FISH_DESIGNS[2]` (frames 0 and 1) and `FISH_DESIGNS[9]` (frame 0), the colour mask runs out before the shape does, so the last one to three characters of those rows fall through to the entity default and render white. The two frames of design 2 are also asymmetric mirrors — one has four backslashes where the other has three slashes — so it is not obvious whether the shape or the mask is the wrong side. Needs someone to look at it in a terminal, which is why the new art test asserts row *counts* and not row *widths*. | planned |
| 32 | **A pre-release on PyPI silently disables the notice.** `parse_version` returns `(0, 0, 0)` for anything non-numeric, so if PyPI ever serves `2.4.0rc1` the comparison reads it as older than everything and no upgrade is ever announced. Harmless today because releases are plain semver; a one-line guard, or ignore pre-releases deliberately. | planned |
| 33 | **The prepare job's premise about retriggering is wrong.** `release_version.py check` documents itself as tolerating the re-run caused when prepare pushes the bump back to the branch. Pushes made with `GITHUB_TOKEN` do not trigger workflow runs, so that second run does not happen — the idempotence is still worth having, but the comment explains something that cannot occur. Separately, `prepare` cannot work from a fork: `pull_request` grants a read-only token there, so the push step fails. Both are documentation fixes, not behaviour ones. | planned |

## In flight

| # | Item | Status |
|---|---|---|
| 23 | **PR #7 — interactive fish feeding.** Not merged as submitted: it did not import on Python 3.8 (`-> tuple[str, str]`), took `ruff` from 0 to 11 findings and `mypy` from 0 to 16, and bundled four features under a one-feature title — one of them (`e`) bound but undocumented — plus a README section and five binary assets belonging to a different repository. The **feeding mechanic underneath was worth keeping** and has landed reworked, with attribution, on `feat/fish-feeding`. The remaining question for the author is Happy Fish mode. | feeding landed |
| 24 | **Happy Fish mode, if it comes back.** PR #7's version recoloured every creature on screen every 200 ms for ten seconds with no way to turn it off, which is the reason it did not land with the feeding. It is a fun idea and the rejection was about the rate, not the concept. Wanted: a capped change rate, off by default or at least interruptible, and no full-body recolour of every entity every frame — that path rebuilt a complete colour mask per shape frame per entity per frame. | open question |

## Rejected on purpose

- **A config file for speeds, colours, and spawn rates.** The ported constants are the
  original's feel. A settings layer nobody has asked for turns one number into a schema, a
  parser, a search path, and a migration story.
- **An entity plugin system.** `RANDOM_OBJECTS` is a list of functions; adding a creature is
  appending to it. An interface with one implementation would be strictly more code.
- **Replacing `curses` with a TUI framework.** Textual or Rich would each add a dependency
  tree to a package that currently has one platform-gated dependency, in exchange for
  abstractions this app does not use.
- **Rendering to anything but a terminal.** GIF export, a web build, and a screensaver mode
  have all been imagined and none have been requested.
- **Mass-annotating the codebase to satisfy `disallow_untyped_defs`.** The flag is off on
  purpose; a diff touching every function to add `-> None` buries the changes that matter.
- **Documenting external hardware or gesture controllers in this README.** Raised by PR #7.
  Anything that drives the aquarium by sending it keystrokes needs nothing from this repo
  and should document itself in its own. A link in the README's Links section is the right
  amount of support; a section plus binary assets is not.
- **Unbounded strobing or full-screen colour cycling.** Also raised by PR #7. Effects that
  change colour across a large area faster than roughly 3 Hz sit in the range associated
  with photosensitive seizures. Rate-capped and off by default is a feature; unbounded and
  always on is not something to ship to people who installed a screensaver on a whim.
