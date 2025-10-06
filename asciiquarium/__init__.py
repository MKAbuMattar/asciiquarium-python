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

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__original_author__",
    "__original_project__",
]

from .main import main

__all__ = ["main"]
