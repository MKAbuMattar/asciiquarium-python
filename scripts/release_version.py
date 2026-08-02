#!/usr/bin/env python3
"""Version bookkeeping for a release.

The version lives in exactly two files. Everything else in the package reads
`__version__` at runtime, and the README's PyPI badge is served live by
shields.io, so those two plus the changelog are the whole job.

    release_version.py current          what this checkout says
    release_version.py status           local vs what is actually on PyPI
    release_version.py check   2.3.0    would this be a legal next version?
    release_version.py apply   2.3.0    write it to the two files + changelog
    release_version.py notes   2.3.0    changelog section, for the release body
    release_version.py verify  2.3.0    wait until PyPI really serves it

`check` is separate from `apply` so the pipeline can reject a bad version
before it has written anything, and `verify` is separate from both so a
publish that silently uploaded nothing cannot report success.
"""

import argparse
import datetime
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION_PY = ROOT / "asciiquarium" / "__version__.py"
PYPROJECT = ROOT / "pyproject.toml"
CHANGELOG = ROOT / "CHANGELOG.md"
REPO = "https://github.com/MKAbuMattar/asciiquarium-python"

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
VERSION_PY_RE = re.compile(r'^(__version__ = ")([^"]+)(")$', re.MULTILINE)
# Anchored to the [project] table's own version, not any dependency pin.
PYPROJECT_RE = re.compile(r'^(version = ")([^"]+)(")$', re.MULTILINE)


def parse(version: str) -> Tuple[int, int, int]:
    match = SEMVER.match(version)
    if not match:
        raise SystemExit(f"error: {version!r} is not MAJOR.MINOR.PATCH")
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def current() -> str:
    match = VERSION_PY_RE.search(VERSION_PY.read_text())
    if not match:
        raise SystemExit(f"error: no __version__ found in {VERSION_PY}")
    return match.group(2)


def _both_files_agree(expected: str) -> None:
    declared = PYPROJECT_RE.search(PYPROJECT.read_text())
    if not declared or declared.group(2) != expected:
        raise SystemExit(
            f"error: pyproject.toml says {declared and declared.group(2)!r} but "
            f"__version__.py says {expected!r}. Reconcile them before releasing."
        )


def check(version: str) -> None:
    """Is `version` a legal target? Idempotent: already-there is not an error.

    The prepare job pushes its bump back to the pull request branch, which
    retriggers the workflow. On that second run the files already say the
    target version, and treating that as a failure would make every release
    red on its own follow-up run.
    """
    new = parse(version)
    old_raw = current()
    old = parse(old_raw)

    if new < old:
        raise SystemExit(
            f"error: {version} is older than the current {old_raw}.\n"
            f"       Rename the branch to release/<a version above {old_raw}>."
        )

    _both_files_agree(old_raw)
    print(f"ready: already at {version}" if new == old else f"bump: {old_raw} -> {version}")


def assert_at(version: str) -> None:
    """Hard gate for the publish job: the tree must already be at `version`."""
    here = current()
    if here != version:
        raise SystemExit(
            f"error: refusing to publish. The branch asks for {version} but this tree is at {here}."
        )
    _both_files_agree(version)
    print(f"tree is at {version}")


def _sub(path: pathlib.Path, pattern: "re.Pattern[str]", version: str) -> None:
    text = path.read_text()
    new_text, count = pattern.subn(rf"\g<1>{version}\g<3>", text, count=1)
    if count != 1:
        raise SystemExit(f"error: expected exactly one version line in {path}")
    path.write_text(new_text)


def apply(version: str) -> None:
    check(version)

    if current() == version:
        print(f"nothing to do, already at {version}")
        return

    _sub(VERSION_PY, VERSION_PY_RE, version)
    _sub(PYPROJECT, PYPROJECT_RE, version)

    text = CHANGELOG.read_text()
    today = datetime.date.today().isoformat()

    # Leave an empty Unreleased behind so the next change has somewhere to go.
    if "## [Unreleased]" not in text:
        raise SystemExit("error: CHANGELOG.md has no '## [Unreleased]' heading")
    text = text.replace(
        "## [Unreleased]",
        f"## [Unreleased]\n\n## [{version}] - {today}",
        1,
    )

    # Repoint the Unreleased compare link and add this release's tag link.
    text = re.sub(
        r"^\[Unreleased\]: .*$",
        f"[Unreleased]: {REPO}/compare/v{version}...HEAD\n"
        f"[{version}]: {REPO}/releases/tag/v{version}",
        text,
        count=1,
        flags=re.MULTILINE,
    )

    CHANGELOG.write_text(text)
    print(f"bumped to {version} in {VERSION_PY.name}, {PYPROJECT.name}, {CHANGELOG.name}")


def notes(version: str) -> None:
    """Print this version's changelog section, for the GitHub Release body."""
    text = CHANGELOG.read_text()
    match = re.search(
        rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    body = (match.group(1).strip() if match else "").strip()
    print(body or f"Release {version}.")


def published() -> Optional[str]:
    """What PyPI is serving right now, or None if it cannot be reached.

    Reuses the package's own checker rather than opening a second HTTP path,
    so a change to how the app talks to PyPI is exercised by the release too.
    """
    sys.path.insert(0, str(ROOT))
    from asciiquarium.version_checker import get_latest_version

    return get_latest_version()


def status() -> None:
    local = current()
    live = published()

    print(f"  this checkout : {local}")
    print(f"  on PyPI       : {live or 'unreachable'}")

    if live is None:
        print("\n  Could not reach PyPI — offline, or the request timed out.")
    elif live == local:
        print(f"\n  In step. v{local} is the published release.")
    elif parse(local) > parse(live):
        print(f"\n  Ahead by {parse(local)[0] - parse(live)[0]} major / unreleased:")
        print(f"  v{local} is staged here but PyPI still serves v{live}.")
    else:
        print(f"\n  Behind. PyPI has v{live}; this checkout is v{local}.")


def is_on_pypi(version: str) -> bool:
    """Does this exact version exist on PyPI?

    Asks the per-version URL rather than reading `info.version` off the project
    endpoint. That aggregate document is CDN-cached and lags: after 2.3.0 went
    out it kept reporting 2.2.0 for minutes while the release was already
    installable. Polling it means a good publish can be reported as a failure.
    """
    url = f"https://pypi.org/pypi/asciiquarium/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return bool(200 <= response.status < 300)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    except (urllib.error.URLError, TimeoutError):
        return False


def verify(version: str, attempts: int = 10, delay: float = 6.0) -> None:
    """Block until PyPI has `version`, so a no-op upload cannot pass.

    An upload can exit 0 and serve nothing, so the release is not finished
    until PyPI answers for this exact version.
    """
    for attempt in range(1, attempts + 1):
        try:
            if is_on_pypi(version):
                print(f"PyPI has {version}")
                return
            note = "not on PyPI yet"
        except urllib.error.HTTPError as exc:
            # A 5xx means PyPI is unwell, not that the upload failed. Keep
            # polling; if it never clears, the loop still ends in a failure.
            note = f"PyPI returned {exc.code}"

        print(f"  attempt {attempt}/{attempts}: {note}", flush=True)
        if attempt < attempts:
            time.sleep(delay)

    raise SystemExit(
        f"error: PyPI never served {version} after {attempts} attempts.\n"
        f"       The upload may have failed silently — check the publish step."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("current")
    sub.add_parser("status")
    for name in ("check", "apply", "notes", "verify", "assert"):
        sub.add_parser(name).add_argument("version")

    args = parser.parse_args()
    if args.command == "current":
        print(current())
    elif args.command == "status":
        status()
    else:
        {
            "check": check,
            "apply": apply,
            "notes": notes,
            "verify": verify,
            "assert": assert_at,
        }[args.command](args.version)


if __name__ == "__main__":
    sys.exit(main())
