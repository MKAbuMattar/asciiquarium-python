import json
import urllib.request
from typing import Optional, Tuple
from urllib.error import URLError

from .__version__ import __version__


def get_latest_version() -> Optional[str]:
    try:
        url = "https://pypi.org/pypi/asciiquarium/json"
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read().decode())
            return data["info"]["version"]
    except (URLError, json.JSONDecodeError, KeyError, TimeoutError):
        return None


def parse_version(version: str) -> Tuple[int, ...]:
    try:
        return tuple(int(x) for x in version.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def is_newer_version(current: str, latest: str) -> bool:
    return parse_version(latest) > parse_version(current)


def check_for_updates(silent: bool = False) -> Optional[str]:
    latest_version = get_latest_version()

    if latest_version is None:
        return None

    if is_newer_version(__version__, latest_version):
        if not silent:
            print("\n")
            print(
                "╔═════════════════════════════════════════════════════════════════════╗"
            )
            print(
                "║                                                                     ║"
            )
            print(
                "║    o      ><>         NEW VERSION AVAILABLE!         <><      o     ║"
            )
            print(
                "║                                                                     ║"
            )
            print(
                "║          <°))))><         v{:<10}          ><(((°>              ║".format(
                    latest_version
                )
            )
            print(
                "║                                                                     ║"
            )
            print(
                "║       Current: v{:<10}      →      Latest: v{:<10}          ║".format(
                    __version__, latest_version
                )
            )
            print(
                "║                                                                     ║"
            )
            print(
                "║    °  Upgrade with:                                                 ║"
            )
            print(
                "║                                                                     ║"
            )
            print(
                "║         pipx install --upgrade asciiquarium                         ║"
            )
            print(
                "║                            or                                       ║"
            )
            print(
                "║         pip install --upgrade asciiquarium                          ║"
            )
            print(
                "║                                                                     ║"
            )
            print(
                "║            ><>      <><      ><>      <><      ><>                  ║"
            )
            print(
                "╚═════════════════════════════════════════════════════════════════════╝\n"
            )
        return latest_version

    return None


def get_update_message() -> str:
    latest_version = get_latest_version()

    if latest_version and is_newer_version(__version__, latest_version):
        return f"💡 v{latest_version} available (current: v{__version__}) - pip install --upgrade asciiquarium"

    return ""
