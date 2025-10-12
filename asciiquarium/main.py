import argparse
import platform
import signal
import sys
import threading

from .__version__ import (
    __author__,
    __email__,
    __license__,
    __original_author__,
    __original_project__,
    __version__,
)
from .animation import Animation
from .entities import (
    add_all_fish,
    add_all_seaweed,
    add_castle,
    add_environment,
    random_object,
)
from .version_checker import check_for_updates


def setup_aquarium(anim: Animation, classic_mode: bool = False):
    """Initialize all aquarium entities"""
    add_environment(anim)
    add_castle(anim)
    add_all_seaweed(anim)
    add_all_fish(anim, classic_mode)
    random_object(None, anim)


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    if sig == signal.SIGINT:
        sys.exit(0)
    elif sig == signal.SIGWINCH:
        pass
    else:
        sys.exit(1)


def show_info():
    """Display information about asciiquarium"""
    info_text = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║   🐠 Asciiquarium {__version__} - ASCII Art Aquarium Animation                ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝

An aquarium/sea animation in ASCII art for your terminal!

FEATURES:
  🐟 Multiple fish species with different sizes and colors
  🦈 Sharks that hunt small fish
  🐋 Whales with animated water spouts
  🚢 Ships sailing on the surface
  🐙 Sea monsters lurking in the depths
  🌊 Animated blue water lines and seaweed
  🏰 Castle decoration
  💙 Blue bubbles rising from fish
  🎨 Full color support
  ⌨️  Interactive controls

CONTROLS:
  Q or q  - Quit the aquarium
  P or p  - Pause/unpause animation
  R or r  - Redraw and respawn entities
  I or i  - Show/hide info screen (press I or ESC to return)

REQUIREMENTS:
  • Python 3.7 or higher
  • Terminal with color support
  • Minimum terminal size: 80x24

PLATFORM SUPPORT:
  ✓ Windows (with windows-curses)
  ✓ Linux (built-in curses)
  ✓ macOS (built-in curses)

CREDITS:
  Python Port     : {__author__} <{__email__}>
  Original Author : {__original_author__}
  Original Project: {__original_project__}

LICENSE:
  {__license__}

LINKS:
  PyPI       : https://pypi.org/project/asciiquarium/
  GitHub     : https://github.com/MKAbuMattar/asciiquarium-python
  Website    : https://mkabumattar.com/

Enjoy your ASCII aquarium! 🐠🐟🦈🐋
"""
    print(info_text)


def get_version_info():
    """Get detailed version information in AWS CLI style"""
    python_version = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    system = platform.system()
    release = platform.release()
    machine = platform.machine()

    version_string = f"asciiquarium/{__version__} Python/{python_version} {system}/{release} {machine}"
    return version_string


class VersionAction(argparse.Action):
    """Custom action to display version info in AWS CLI style"""

    def __call__(self, parser, namespace, values, option_string=None):
        print(get_version_info())
        parser.exit()


def create_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        prog="asciiquarium",
        description="🐠 An aquarium/sea animation in ASCII art for your terminal",
        epilog="Enjoy your ASCII aquarium! 🐠🐟🦈",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v",
        "--version",
        action=VersionAction,
        nargs=0,
        help="Show version information and exit",
    )

    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Show detailed information about asciiquarium",
    )

    parser.add_argument(
        "-c",
        "--classic",
        action="store_true",
        help="Classic mode - use only original fish and monster designs",
    )

    parser.add_argument(
        "--check-updates",
        action="store_true",
        help="Check for available updates and exit",
    )

    return parser


def main():
    """Main entry point for the asciiquarium application"""
    parser = create_parser()
    args = parser.parse_args()

    if args.info:
        show_info()
        sys.exit(0)

    if args.check_updates:
        print("Checking for updates...")
        latest = check_for_updates(silent=False)
        if latest is None:
            print("✓ You are running the latest version!")
        sys.exit(0)

    update_thread = threading.Thread(target=check_for_updates, daemon=True)
    update_thread.start()

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGWINCH"):
        signal.signal(signal.SIGWINCH, signal_handler)

    try:
        anim = Animation()

        def setup_with_mode(anim_instance):
            return setup_aquarium(anim_instance, args.classic)

        anim.run(setup_with_mode)
    except ImportError as e:
        if "curses" in str(e).lower():
            print(f"Error: {e}", file=sys.stderr)
            if sys.version_info >= (3, 13) and platform.system() == "Windows":
                print("\nFor Python 3.13+ on Windows, try:", file=sys.stderr)
                print("  pip install windows-curses", file=sys.stderr)
                print("  or use Python 3.12 or earlier", file=sys.stderr)
            sys.exit(1)
        else:
            raise
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        update_thread.join(timeout=0.5)


def cli_main():
    """CLI entry point alias"""
    main()


if __name__ == "__main__":
    main()
