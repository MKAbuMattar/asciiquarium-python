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
| 1 | **The update check can corrupt the screen.** `main()` starts `check_for_updates` on a daemon thread and then hands the terminal to curses. If PyPI answers within its 2-second timeout and a newer version exists, the thread prints a 20-line box straight into the curses screen. Nothing can repaint over it because curses does not know it happened. Check before `curses.wrapper`, or stash the result and print it after `endwin()`. | planned |
| 2 | **Frame rate is whatever the keyboard says it is.** There is no frame clock: pacing comes from `curses.halfdelay(1)` blocking for 100ms in `getch()`. A keypress returns immediately, so holding any key runs the aquarium at keyboard-repeat speed. Drive the loop from a monotonic deadline and keep `halfdelay` only for input. | planned |
| 3 | **Multi-frame entities report the wrong size.** `Entity._update_dimensions` measures `shapes[0]` only, but `size()` feeds both collision detection and the `die_offscreen` test. The whale, the sea monsters, and the ducks all have frames of differing widths, so they are culled and collide against a stale box. Measure the max across every frame. | planned |
| 4 | **Resize leaves the scene stale.** `KEY_RESIZE` updates `screen_width`/`screen_height` and nothing else. Waterlines stay tiled to the old width, the castle stays anchored to the old right edge, and `update_term_size`'s too-small `ValueError` is swallowed by the bare `except Exception` in the input handler. Rebuild the scene on resize — the `r` key already does exactly this. | planned |
| 5 | **Two one-token bugs.** `special.py` sets `default_color="blue"` lowercase on the lead dolphin; `color_pairs` is keyed uppercase, so it renders uncoloured. `asciiquarium/__init__.py` assigns `__all__` twice, and the second assignment silently drops every version symbol the first one exported. | planned |
| 6 | **`__init__.py` shadows its own submodule.** `from .main import main` rebinds the name `main` on the package, so `import asciiquarium.main as m` hands back the *function*, not the module, and `python -m asciiquarium.main` warns about it. The console script still resolves, which is why nobody has noticed. Import the module and re-export deliberately, or drop the convenience import. | planned |

## Phase 2 — Nothing verifies any of this

| # | Increment | Status |
|---|---|---|
| 7 | **CI.** `.github/workflows/validate.yml` runs `ruff`, `mypy`, an import sweep and CLI smoke check across every supported Python version, a build, and a check that `__version__.py` and `pyproject.toml` agree. Both linters report zero findings on `main`, so the gate is meaningful from day one: anything red was introduced by the change under review. Nothing had ever been checked automatically before. | ✅ done |
| 8 | **A smoke test.** `pytest` is a declared dev dependency and there are zero test files. The renderer needs a TTY, but the parts that actually break do not: `Entity` sizing and death conditions, `parse_version`/`is_newer_version`, `rand_color` leaving no stray digits, and every shape/colour-mask pair in the entity modules having matching line counts. That last one is a real test — mask misalignment is this codebase's most common silent failure. Wire it into the existing workflow. | planned |

## Phase 3 — Consolidation

| # | Increment | Status |
|---|---|---|
| 9 | **One formatter, one linter.** `black`, `isort`, and `ruff` are all configured, and `ruff` already does both other jobs (`"I"` is in the selected rule set). The two configs disagree: `isort` sets `line_length = 88`, `ruff` sets `line-length = 100`. Collapse onto `ruff format` + `ruff check --fix`. Note that `ruff format --check` currently *fails* on `main` — the tree is black-formatted at a different width, so this lands as one reformat commit and only then becomes a CI gate. | planned |
| 10 | **One dev-dependency list.** Dev deps are declared three times — `[project.optional-dependencies].dev`, `[tool.hatch.envs.default]`, and an empty `[dependency-groups].dev` — with conflicting bounds (`mypy>=1.0.0` in one, `mypy<1.5.0` in the other). Keep one. | planned |
| 11 | **`[tool.mypy] python_version = "3.8"` is rejected by current mypy.** Every run prints `Python 3.8 is not supported (must be 3.10 or higher)` before doing anything. It still exits 0, so it looks fine and is easy to miss — but the version the config asks for is not the version being checked. Blocked on (19). | planned |
| 12 | **Deduplicate the colour randomiser.** `rand_color()` exists in `fish.py`; `special.py` inlines the identical twelve-colour loop twice for the two big fish. Import the function. | planned |
| 13 | **Deduplicate the info screen.** The feature list, controls, and credits are written out twice: `main.show_info()` for `--info` and `Animation.show_info_overlay()` for the `i` key. They have already drifted — the CLI version claims Python 3.7 and an 80×24 minimum; the code enforces 3.8 and 40×15. Build both from one source. | planned |
| 14 | **Name the waterline constant.** `9` — the first row a fish may occupy — is hardcoded in five places across three modules, sometimes as `9`, sometimes as `height() - 9`. One named constant next to `DEPTH`. | planned |
| 15 | **Break the import cycle.** `entities/*` imports `DEPTH` from `animation`, so `animation` cannot import `entities` at module level. Anything needing to spawn an entity from the animation layer has to do a function-local import. Move `DEPTH` (and the waterline constant from 14) into their own module that both sides import. | planned |
| 16 | **Delete what is already dead.** `MANIFEST.in` (hatchling ignores it), the `SIGWINCH` handler in `main()` (ncurses installs its own during `initscr`, after this one, so it never fires), the `callback_args == "hooked"` string branch in `fishhook_cb`, the unused `position()` call in `retract()`, and the `elif showing_info: pass` no-op in the run loop. | planned |

## Phase 4 — Quality

| # | Increment | Status |
|---|---|---|
| 17 | **The renderer draws one character at a time.** `_draw_entity` calls `addch` per cell with a per-cell colour lookup and three `try` frames. At 200×50 that is up to 10,000 calls per frame. Batching each run of same-coloured characters into one `addstr` is the same output with an order of magnitude fewer calls, and it is what makes a higher frame rate affordable once (2) lands. | planned |
| 18 | **The info overlay does not fit its own minimum terminal.** Its box is 73 columns of hardcoded rule and it runs ~35 lines, but the enforced minimum is 40×15. Below ~75 columns every line is truncated mid-box; below ~35 rows the bottom is cut off, including "press I or ESC to return". Reflow to the available width, or state a real minimum for the overlay and show a short form under it. | planned |
| 19 | **Drop Python 3.8.** It is past end-of-life, it is what pins `typing.List`/`Dict` throughout, and `windows-curses` is already special-cased around version boundaries. Moving to 3.9+ costs nothing, removes a column from the CI matrix, and unblocks (11). | planned |
| 20 | **Ship `py.typed`.** The package is annotated and `mypy` is configured, but without the marker no downstream consumer sees any of it. | planned |
| 21 | **Colour is the only channel.** Creatures are distinguished purely by hue, and `init_pair` failures are swallowed, so a 8-colour or monochrome terminal degrades silently rather than falling back deliberately. Nothing here encodes meaning yet, so this is not urgent — but it is worth settling before anything does. | planned |
| 22 | **Release workflow.** Publishing is manual today. A tag-triggered workflow using PyPI trusted publishing removes the local-token step — deliberately not written yet, because it needs the publisher configured on PyPI first and a workflow that cannot authenticate is worse than none. | planned |

## In flight

| # | Item | Status |
|---|---|---|
| 23 | **PR #7 — interactive fish feeding.** The feeding mechanic is worth having: mouth-position hit detection and directional food preference are more considered than the feature needed. It cannot merge as it stands. It does not import on Python 3.8 (`-> tuple[str, str]` at `animation.py:416`), it takes `ruff` from 0 to 11 findings and `mypy` from 0 to 16, and its Happy Fish mode recolours the whole screen every 200 ms for ten seconds with no opt-out — see the accessibility note in `.github/CONTRIBUTING.md`. It is also four features under a one-feature title, one of which (`e`) is bound but undocumented, plus a README section and five binary assets belonging to a different repository. Ask for a split: feeding alone first, Happy Fish behind a rate cap second, the overlay refactor third and only if it actually fixes (18). | changes requested |

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
