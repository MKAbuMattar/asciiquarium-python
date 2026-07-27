# Contributing

Thanks for wanting to improve the aquarium.

This is a small package: one dependency, no build step, no test suite yet. That makes it
easy to contribute to and easy to break in ways nobody notices until a user opens a
terminal. Most of what follows is about the second half of that sentence.

## Setup

```bash
git clone https://github.com/MKAbuMattar/asciiquarium-python
cd asciiquarium-python
uv sync            # or: pip install -e ".[dev]"
uv run asciiquarium
```

## Before you open a pull request

```bash
uvx ruff check asciiquarium
uvx mypy --ignore-missing-imports asciiquarium
```

Both report **zero findings on `main`**. If either one reports something, it came from your
change. CI runs the same two commands.

## Verifying a change you cannot see in a diff

A curses app has no snapshot to compare. Reading the diff tells you nothing about whether
the screen is right. Run it, and run it in the awkward cases:

1. **80×24, then 40×15.** Forty columns is the enforced minimum and it is where clipping
   bugs live.
2. **`--classic`.** It takes a different branch through `add_fish` and `add_monster`, so
   half the art never renders without it.
3. **Press `r` a few times.** It tears down and rebuilds every entity — resize and
   lifecycle bugs surface here.
4. **`TERM=xterm asciiquarium`.** Colour-pair setup failures are swallowed silently, so a
   change that assumes 256 colours degrades without any error.

Write down which of these you did in the PR template. "Lint passes" is not verification.

## Working with the ASCII art

Every entity carries two parallel strings: the **shape** and the **colour mask**. They are
indexed by the same row and column — `color[y][x]` colours `shape[y][x]`.

```python
shape = "  __\n><_'>\n   '"
color = "  11\n61145\n   3"     # aligned column by column
```

Three things follow from that, and all three fail silently:

- **Alignment is positional, not semantic.** Insert one space into a shape line without
  inserting one into the matching colour line and the rest of that row is recoloured.
- **Digits `1`–`9` in a mask are placeholders**, not colours. `rand_color()` swaps each
  digit for a random colour letter so two fish of the same design look different. A literal
  digit reaching the renderer is a bug in your mask.
- **Colour names are uppercase.** `default_color="blue"` does not raise — it renders with
  no colour at all. (There is one of these on `main` today.)

Shapes are full of backslashes. Use `r"""..."""` for new art.

## Adding a creature

`RANDOM_OBJECTS` in `asciiquarium/entities/special.py` is a plain list of spawner functions.
Append yours. Each spawner sets `death_cb=random_object` so that when its entity leaves the
screen it spawns the next one — **the population is self-sustaining through death callbacks,
not a scheduler.** Break that chain and the aquarium empties out and stays empty.

Give your entity an explicit `entity_type` if anything else needs to find it via
`get_entities_of_type`.

## Scope

**One PR, one thing.** A branch carrying a feature plus an unrelated refactor plus a README
section is slower to review than the sum of its parts, and one blocking problem in any part
of it holds up all the rest.

Specifically, please don't:

- Document another project in this README. Link to it from your own repo instead.
- Commit binary assets that belong to a different project.
- Add a keybinding without documenting it in both the README and the in-app info overlay.
- Leave superseded iterations of your own work in the diff (`do_thing`, `do_thing_v2`,
  `do_thing_v3`). Ship the one that wins.

If you are unsure whether something is in scope, open an issue first. That is cheaper than
finding out after you have written it.

## Matching the original

This is a port of Kirk Baucom's Perl asciiquarium. Speeds, spawn offsets, and probabilities
(`random.randint(1, 100) > 97` for bubbles, and so on) are ported values, not invented ones.
Changing one changes the feel of the aquarium — that's allowed, but call it out in the PR
and in `CHANGELOG.md` so it is a decision rather than a drift.

## Accessibility

Rapid full-screen colour cycling is not a free effect. Anything that changes colour or
brightness across a large area more than about three times per second sits in the range
associated with photosensitive seizures. If you add a flashing or strobing effect, cap the
rate, keep it off by default, and make it possible to turn off.

## Commits

Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.

No `Co-Authored-By` trailer, no "Generated with …", no AI-assistant attribution of any kind
in the subject or body.

## Licence

GPL-3.0-or-later, inherited from the original. Contributions are accepted under the same
licence. Don't add a dependency under an incompatible one.
