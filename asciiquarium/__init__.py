"""
Asciiquarium - An aquarium animation in ASCII art

This package provides a terminal-based ASCII art aquarium animation
that works cross-platform on Windows, Linux, and macOS.

Author: Mohammad Abu Mattar (info@mkabumattar.com)
Website: https://mkabumattar.com/
"""

from .__version__ import (
    __author__,
    __email__,
    __license__,
    __original_author__,
    __original_project__,
    __version__,
)

# No `from .main import main` here: it rebound the name `main` on the package,
# so `import asciiquarium.main` handed back the function instead of the module.
# The console script resolves `asciiquarium.main:main` through importlib and is
# unaffected. Importing the package also no longer pulls in curses.
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__original_author__",
    "__original_project__",
]
