<!-- What does this change, and why? One or two lines. -->

## Summary

## How you verified it

This is a curses app — **a passing lint run is not evidence that it renders correctly.**
Tell us what you actually watched:

- Terminal emulator and OS:
- `$TERM` and terminal size:
- Ran with `--classic` too:  yes / no

## Checklist

- [ ] `uvx ruff check asciiquarium` passes (it reports zero findings on `main`)
- [ ] `uvx mypy --ignore-missing-imports asciiquarium` passes (also clean on `main`)
- [ ] Ran it at 80×24 **and** at the 40×15 minimum — nothing clipped or misaligned
- [ ] Pressed `r` to force a full teardown and rebuild
- [ ] New or edited ASCII art: the colour mask lines are aligned to the shape **column by
      column**, and the two have the same number of lines
- [ ] New colour names are uppercase (`"BLUE"`, not `"blue"` — lowercase silently renders
      uncoloured)
- [ ] Runs on the oldest supported Python in `requires-python`, not just yours
- [ ] No new dependency (`windows-curses` is the only one, and it is platform-gated)
- [ ] Nothing writes to stdout while the animation is running
- [ ] New keybindings are documented in the README **and** the in-app info overlay
- [ ] `CHANGELOG.md` updated if a user would notice the change
- [ ] Version bumped in `asciiquarium/__version__.py` **and** `pyproject.toml` if releasing
- [ ] Conventional-commit messages, no `Co-Authored-By` / AI-assistant trailer

## Scope

- [ ] This PR does **one** thing. Unrelated features, refactors, and README sections about
      other projects belong in separate PRs — they are much slower to review together and
      one blocking problem holds up everything else in the branch.
- [ ] No binary files unless the change genuinely needs them, and none that document a
      different repository.
