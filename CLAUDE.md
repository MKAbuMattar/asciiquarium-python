# asciiquarium

Agent instructions for this repo live in **@AGENTS.md** — read it first. It covers what this
is, the module layout, the two parallel string grids (shape + colour mask) that every entity
is built from, the depth and coordinate conventions, the death-callback lifecycle that keeps
the aquarium populated, the working commands, and the hard rules (lint passes, version bumped
in one place, changelog entry, clean conventional commits).

## Before changing anything visual

This is a curses app: **you cannot verify it by reading the diff.** Run it in a real terminal
at 80×24 and at the 40×15 minimum, with and without `--classic`, and press `r` to force a
full rebuild. `AGENTS.md` has the checklist.

## The one rule that bites hardest

Shapes and colour masks are two separate strings indexed by the same `[row][column]`. Editing
ASCII art without editing the mask underneath it in the same columns is the most common way
to break this codebase, and it fails silently.

Keep this file thin: put durable instructions in `AGENTS.md`, not here.
