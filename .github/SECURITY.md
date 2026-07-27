# Security Policy

## Supported versions

Fixes land on the latest release published to
[PyPI](https://pypi.org/project/asciiquarium/). There are no maintained release branches —
please upgrade before reporting.

```bash
pipx upgrade asciiquarium    # or: pip install --upgrade asciiquarium
```

## Reporting

Report privately through
[GitHub Security Advisories](https://github.com/MKAbuMattar/asciiquarium-python/security/advisories/new).
Please don't open a public issue for a suspected vulnerability.

Expect an acknowledgement within a few days. Because this is a hobby project maintained in
spare time, a fix may take longer — you'll be told where it stands.

## Realistic scope

This is an ASCII animation. It takes no user input beyond single keypresses, parses no
files, and opens no ports. The attack surface is genuinely small, and the following are the
parts that could matter:

- **The PyPI version check.** `asciiquarium/version_checker.py` makes one outbound HTTPS
  request to `pypi.org` on startup and parses the JSON response. Anything reachable through
  that path — response handling, the 2-second timeout, TLS behaviour — is in scope.
- **The build and release pipeline.** A compromised published artifact is the highest-impact
  scenario here, well above anything in the animation itself.
- **Dependency issues** in `windows-curses`, the one runtime dependency (Windows only).
- **Terminal escape sequence injection**, if any code path can be made to emit attacker-
  controlled bytes to the terminal.

## Out of scope

- Crashes or garbled output from resizing the terminal, or from terminals smaller than the
  40×15 minimum. Those are bugs — please file them as
  [rendering problems](https://github.com/MKAbuMattar/asciiquarium-python/issues/new/choose).
- The animation leaving the terminal in an odd state after an abnormal exit. Also a bug,
  also a regular issue.
- Automated scanner output with no demonstrated impact on this package.
