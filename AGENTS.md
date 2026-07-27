# AGENTS.md — asciiquarium

Instructions for AI agents working in this repo. Human contributors: see `README.md` and
`.github/CONTRIBUTING.md`.

## What this is

A Python reimplementation of Kirk Baucom's Perl [asciiquarium](http://robobunny.com/projects/asciiquarium):
an ASCII-art aquarium that draws to the terminal with `curses`. Shipped to PyPI as
`asciiquarium`, installed as a single console script.

```bash
pipx install asciiquarium && asciiquarium
```

There is **no frontend, no server, no database**. One package, ~2,100 lines, one runtime
dependency (`windows-curses`, Windows only). The output surface is a character grid; the
input surface is single keypresses.

## Layout

- `asciiquarium/main.py` — CLI entry point. `argparse`, signal handling, the update-check
  thread, and the `--info` text screen.
- `asciiquarium/animation.py` — the `Animation` controller: curses init, the colour-pair
  table, the `DEPTH` z-ordering map, collision detection, the draw loop, and the in-app info
  overlay. **The frame loop lives in `Animation.run()`.**
- `asciiquarium/entity.py` — `Entity`, the one model everything on screen uses: shape frames,
  colour-mask frames, position, velocity, death conditions, collision list.
- `asciiquarium/entities/environment.py` — waterlines, castle, seaweed.
- `asciiquarium/entities/fish.py` — the fish designs (classic + new), bubbles, the splat.
- `asciiquarium/entities/special.py` — everything spawned by `random_object()`: shark, ship,
  whale, sea monsters, big fish, fishhook, swan, ducks, dolphins.
- `asciiquarium/version_checker.py` — PyPI version poll.
- `.github/` — CI workflow plus community health files.
- `CHANGELOG.md` / `ROADMAP.md` — what changed, and what is queued next.

## The two parallel string grids

Every entity carries **shapes** and **colours** as two lists of multi-line strings that are
indexed together. `Animation._draw_entity` walks them character by character: `shape[y][x]`
is what gets drawn, `color[y][x]` is a single-character key into `mask_color_map`.

This means:

- **The colour mask must be aligned to the shape by column**, not by content. Adding a space
  to a shape line without adding one to the matching colour line silently recolours the rest
  of that row.
- **Digits `1`–`9` in a colour mask are placeholders**, not colours. `rand_color()` replaces
  each digit with a randomly chosen colour letter so two fish of the same design differ. A
  literal digit that reaches the renderer is a bug in the mask.
- **Colour names are case-sensitive.** `color_pairs` is keyed by the uppercase names in
  `color_map`; `default_color="blue"` silently renders uncoloured.
- Shapes are raw strings full of backslashes. Prefer `r"""..."""` for new art.

## Coordinate and depth conventions

- `y = 0..4` is sky, `y = 5..8` is the waterline band, `y >= 9` is underwater. **`9` is
  hardcoded in five places** as "the first row a fish may occupy" — see the roadmap.
- `DEPTH` in `animation.py` is *two* overlapping scales inherited from the Perl original: a
  GUI/creature scale (`gui`=1, `shark`=2, `fish_start`=3…`castle`=22) and a water scale
  (`water_line3`=2 … `water_gap0`=9). Values collide across the two on purpose. Lower `z`
  draws on top (`animate()` sorts descending and paints back to front).

## Entity lifecycle

`random_object()` picks one spawner from `RANDOM_OBJECTS`. Every spawner sets
`death_cb=random_object` (or a wrapper), so when its entity leaves the screen the callback
spawns the next one. **The population is self-sustaining through death callbacks, not a
scheduler.** Break that chain and the aquarium goes empty and stays empty.

Same pattern for fish (`death_cb=add_fish`) and seaweed (`death_cb=add_seaweed`).

## Working commands

| Command | What it does |
|---|---|
| `uv run asciiquarium` | Run it. Needs a real TTY of at least 40×15. |
| `hatch run lint` | `ruff check asciiquarium` then `mypy asciiquarium`. |
| `hatch run fmt` | `isort` then `black` over the package. |
| `uvx pytest -q` | Run the tests. No terminal required. |
| `python -m build` | Build sdist + wheel via hatchling. |
| `python3 scripts/release_version.py status` | This checkout's version vs what PyPI is serving. |
| `grep -rnE '(#\|//) ?ponytail:' .` | Deferred-shortcut ledger. |

There is no test suite yet. **Verifying a change means running it in a terminal and
watching it**, which is why the PR template asks which terminal you watched it in.

## Testing a rendering change

A curses app cannot be diffed. When changing the renderer, art, or colour masks:

1. Run at 80×24 and at the 40×15 minimum. Small terminals are where clipping bugs live.
2. Run with `--classic` too; it takes a different branch through `add_fish` and `add_monster`.
3. Press `r` a few times. It tears down and rebuilds every entity, which is where
   resize/rebuild bugs surface.
4. Check a terminal without 256 colours (`TERM=xterm`) — `init_pair` failures are swallowed.

## Conventions

- **Match the Perl original's behaviour unless there's a reason not to.** Speeds,
  probabilities (`random.randint(1, 100) > 97` for bubbles), and spawn offsets are ported
  values, not invented ones. Changing one changes the feel; say so in the changelog.
- **Never let anything but curses write to stdout while the animation runs.** A stray
  `print` from a background thread corrupts the screen and there is no way to recover it.
- **`_draw_entity` is the hot path.** It runs per character, per entity, per frame. Anything
  added inside its inner loop is multiplied by roughly `width × height × entities × fps`.
- **Type hints on new code**, but `disallow_untyped_defs` is off — don't mass-annotate
  untouched functions in an unrelated change.
- Keep the package dependency-free on Linux and macOS. `windows-curses` is the one
  exception and it is platform-gated in `pyproject.toml`.

## Releasing

Never bump the version by hand — `.github/workflows/release.yml` owns it.

```bash
git switch -c release/2.3.0        # the branch name IS the version
git push -u origin release/2.3.0
gh pr create --base main --label release --title "Release v2.3.0"
```

Adding the `release` label starts the `prepare` job: it rewrites
`asciiquarium/__version__.py` and `pyproject.toml`, rolls `CHANGELOG.md`'s
`## [Unreleased]` into a dated section, pushes that commit back to your branch, runs the
full gate, builds, and installs the wheel to check it actually runs. It then comments on the
pull request with what merging will do.

**Merging the pull request publishes to PyPI.** That is the irreversible step, and it is
deliberately the only one: PyPI does not allow re-uploading a version, so a mistaken merge
burns that version number permanently. The `publish` job re-checks that the merged tree
carries the version its branch name promises, uploads, polls PyPI until it is really being
served, tags `v2.3.0`, and writes the Release page.

The version must be strictly newer than the current one; the pipeline refuses otherwise.
Preparation is idempotent, so pushing more commits to the branch re-runs it safely.

`python3 scripts/release_version.py` does all the version bookkeeping and is worth running
locally — `status` compares this checkout against PyPI, `check 2.3.0` tells you whether a
version would be accepted before you push anything.

## Hard rules

- **`uvx ruff check asciiquarium tests` and `uvx mypy --ignore-missing-imports asciiquarium`
  must pass** before commit. Both are clean on `main`, so anything they report is yours.
- **Never edit the version by hand.** `asciiquarium/__version__.py` is the source of truth
  and `pyproject.toml` mirrors it, but the release pipeline is what writes both.
- **Add a `CHANGELOG.md` entry** for anything a user would notice.
- **Clean commits.** Conventional-commit subject + body. **No** `Co-Authored-By` trailer,
  **no** "Generated with Claude Code", **no** Opus/Anthropic/AI mention of any kind.
- **Don't commit local tooling.** `.serena/`, `.vscode/settings.local.json`, `__pycache__/`,
  `.venv/`, and `graphify-out/` are local-only.
- **GPL-3.0-or-later.** The original is GPL; this port inherits it. Don't add a dependency
  under an incompatible licence.
- Push only when asked.
