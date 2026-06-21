<div align="center">

# 🐠 Asciiquarium - Python Edition

<div align="center">
  <a href="https://github.com/MKAbuMattar/asciiquarium-python" target="_blank" rel="noreferrer">
    <img src="https://img.shields.io/badge/github-%23181717.svg?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Repository"/>
  </a>

  <a href="https://github.com/MKAbuMattar/asciiquarium-python/releases" target="_blank" rel="noreferrer">
    <img alt="GitHub Release" src="https://img.shields.io/github/v/release/MKAbuMattar/asciiquarium-python?color=%232563eb&label=Latest%20Release&style=for-the-badge&logo=github" />
  </a>

  <a href="https://pypi.org/project/asciiquarium/" target="_blank" rel="noreferrer">
    <img src="https://img.shields.io/pypi/v/asciiquarium?style=for-the-badge&logo=pypi&logoColor=white&color=2563eb&label=PyPI" alt="PyPI Version"/>
  </a>

  <a href="https://pypi.org/project/asciiquarium/" target="_blank" rel="noreferrer">
    <img src="https://img.shields.io/pypi/pyversions/asciiquarium?style=for-the-badge&logo=python&logoColor=white&color=2563eb&label=Python" alt="Python Versions"/>
  </a>

  <a href="/LICENSE" target="_blank" rel="noreferrer">
    <img alt="GPL-3.0 License" src="https://img.shields.io/github/license/MKAbuMattar/asciiquarium-python?color=%232563eb&style=for-the-badge&label=License">
  </a>

  <a href="https://github.com/MKAbuMattar/asciiquarium-python/stargazers" target="_blank" rel="noreferrer">
    <img alt="GitHub Stars" src="https://img.shields.io/github/stars/MKAbuMattar/asciiquarium-python?color=%232563eb&label=Stars&style=for-the-badge&logo=github">
  </a>

  <a href="https://pypi.org/project/asciiquarium/" target="_blank" rel="noreferrer">
    <img alt="PyPI Downloads" src="https://img.shields.io/pypi/dm/asciiquarium?color=%232563eb&style=for-the-badge&logo=pypi&label=Downloads">
  </a>

  <a href="https://github.com/MKAbuMattar/asciiquarium-python/issues" target="_blank" rel="noreferrer">
    <img alt="GitHub Issues" src="https://img.shields.io/github/issues/MKAbuMattar/asciiquarium-python?color=%232563eb&style=for-the-badge&logo=github&label=Issues">
  </a>
</div>

<br/>

[🌐 Website](https://mkabumattar.com/) • [📦 PyPI](https://pypi.org/project/asciiquarium/) • [🚀 Quick Start](#-installation) • [💬 Support](https://github.com/MKAbuMattar/asciiquarium-python/issues)

<br/>

---

An aquarium/sea animation in ASCII art for your terminal! This is a Python reimplementation of the classic Perl asciiquarium, designed to work cross-platform on Windows, Linux, and macOS.

![Asciiquarium](https://github.com/MKAbuMattar/asciiquarium-python/blob/main/.github/assets/asciiquarium.gif)

</div>

## ✨ Features

- 🐟 Multiple fish species with different sizes and colors
- 🦈 Sharks that hunt small fish
- 🐋 Whales with animated water spouts
- 🚢 Ships sailing on the surface
- 🐙 Sea monsters lurking in the depths
- 🌊 Animated blue water lines and seaweed
- 🏰 Castle decoration
- � Blue bubbles rising from fish
- 🎨 Full color support
- ⌨️ Interactive controls
- 🍣 Feeding support: press `F` to drop food into the aquarium.
- 🐟 Fish can detect nearby food, swim toward it, and eat it.
- 👍 "Happy Fish" mode: press `H` to excite the fish.
- 🌍 Cross-platform (Windows, Linux, macOS)

## 🚀 Installation

### Using pip (Standard)

```bash
pip install asciiquarium
```

### Using pipx (Isolated)

[pipx](https://pipx.pypa.io/) installs the package in an isolated environment:

```bash
pipx install asciiquarium
```

## 🎯 Usage

After installation, simply run:

```bash
asciiquarium
```

That's it! Enjoy your ASCII aquarium! 🐠

## 🎮 Controls

- **`Q`** or **`q`** - Quit the aquarium
- **`P`** or **`p`** - Pause/unpause the animation
- **`R`** or **`r`** - Redraw and respawn all entities
- **`I`** or **`i`** - Show/hide info overlay
- **`F`** or **`f`** - Feed the fish
- **`H`** or **`h`** - "Happy Fish" mode for 10 seconds

## � Requirements

- **Python 3.8+** - Works with Python 3.8 through 3.14+
- **Terminal** - Any terminal with color support (minimum 40x15, recommended 80x24)
- **Dependencies** - Automatically handled:
  - `windows-curses` - Auto-installed on Windows (Python < 3.13)
  - `curses` - Built-in on Linux/macOS

### Python 3.13+ Support

For Python 3.13+ on Windows, you may need to install `windows-curses` manually:

```bash
pip install windows-curses
```

If you encounter issues, consider using Python 3.12 or earlier for the most stable experience.

### 🤏 OpenGhost Gesture-Control Note

This fork adds feeding behavior to asciiquarium.

New keyboard control:

```text
F or f    Drop food into the aquarium
H or h    "Happy Fish" mode: 10 seconds of increased activity and color changing
```

When used with the OpenGhost Raspberry Pi controller, the aquarium can also be controlled by hand gestures. Hand gesture support requires the modified OpenGhost controller code from the `pinch-release-keypress` branch of this repository:

```text
https://github.com/klwill1192/OpenGhost/tree/pinch-release-keypress
```
	
```text
Pinch thumb and index finger, then release     Drop food into the aquarium
Hold a "thumbs up" gesture                     Start "Happy Fish" mode for 10 seconds
Hold a two-finger "peace sign" gesture         Quit the aquarium ("Peace out!")
Hold a closed fist gesture                     Shut down the Raspberry Pi
```

The OpenGhost controller displays a small status flag over the castle:

| Flag | Meaning |
|---|---|
| <img src="images/status_flag_no_hand.png" alt="White/gray outline flag" width="24"> | No hand detected by the camera |
| <img src="images/status_flag_green.png" alt="Green flag" width="24"> | Hand detected / normal operation |
| <img src="images/status_flag_magenta.png" alt="Magenta flag" width="24"> | Happy Fish mode was triggered and is active/recent |
| <img src="images/status_flag_yellow.png" alt="Yellow flag" width="24"> | Shutdown gesture has been held for 2 seconds |
| <img src="images/status_flag_red.png" alt="Red flag" width="24"> | Shutdown gesture has been held for 4 seconds; shutdown is imminent |

After the peace sign gesture is held for 5 seconds, OpenGhost sends `q` to the asciiquarium xterm window and exits cleanly. Peace out!

After the closed fist gesture is held for 7 seconds, OpenGhost requests a clean Raspberry Pi shutdown.

## 🌍 Platform Support

| Platform   | Status             | Notes                          |
| ---------- | ------------------ | ------------------------------ |
| 🪟 Windows | ✅ Fully Supported | Auto-installs `windows-curses` |
| 🐧 Linux   | ✅ Fully Supported | Uses built-in `curses`         |
| 🍎 macOS   | ✅ Fully Supported | Uses built-in `curses`         |

## 📦 What Gets Installed

The package includes:

- Main application and animation engine
- All entity types (fish, sharks, whales, ships, etc.)
- ASCII art designs and color schemes
- Cross-platform terminal handling

**Size:** ~50KB (minimal footprint!)

## 🛠️ Development Installation

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/MKAbuMattar/asciiquarium-python.git
cd asciiquarium-python

# Install in editable mode with development dependencies
uv pip install -e ".[dev]"

# Run from source
python -m asciiquarium.main
```

### Development Requirements

Before submitting any changes, ensure your code passes all checks:

```bash
# Run the formatter
uv run hatch run fmt

# Run linters (must pass without errors)
uv run hatch run lint
```

All contributions must pass both formatting and linting checks before being merged.

## 🌟 Features Details

### Cross-Platform Support

This implementation uses Python's `curses` library and automatically installs `windows-curses` on Windows systems, making it truly cross-platform.

### Entity Types

- **Fish**: 7 different species with unique ASCII art designs and swimming patterns
- **Sharks**: Predators that hunt and eat smaller fish with collision detection
- **Whales**: Large creatures with animated water spout effects
- **Ships**: Sail across the surface of the water
- **Sea Monsters**: Mysterious creatures lurking in the depths
- **Big Fish**: Large colorful fish with randomized color schemes
- **Environment**: Seaweed, castle decorations, and blue water lines
- **Bubbles**: Rise from fish in blue color

### Animation Features

- **Smooth Animation**: 30 FPS for fluid motion
- **Z-depth Layering**: Proper entity overlapping
- **Color Masking**: Detailed multi-color ASCII art
- **Frame Animation**: Multi-frame animations for complex entities
- **Collision Detection**: Sharks interact with small fish
- **Auto Cleanup**: Off-screen entities are automatically removed

## 📁 Project Structure

```
asciiquarium-python/
├── asciiquarium/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── entity.py            # Base entity class
│   ├── animation.py         # Animation engine
│   └── entities/
│       ├── __init__.py
│       ├── fish.py          # Fish entities
│       ├── environment.py   # Environment entities
│       └── special.py       # Special entities (sharks, whales, etc.)
├── pyproject.toml
├── uv.lock
└── README.md
```

## 🎨 Customization

You can easily add new entities by creating them in the appropriate module:

```python
from asciiquarium.entity import Entity

def add_my_entity(old_ent, anim):
    anim.new_entity(
        entity_type='my_type',
        shape=my_ascii_art,
        color=my_color_mask,
        position=[x, y, z],
        callback_args=[dx, dy, dz, frame_speed],
        die_offscreen=True,
        death_cb=add_my_entity,
    )
```

## 🐛 Troubleshooting

### Command Not Found

If `asciiquarium` command is not found after installation:

**On Windows:**

```powershell
# Add Python Scripts to PATH
python -m asciiquarium.main
```

**On Linux/macOS:**

```bash
# Make sure ~/.local/bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
asciiquarium
```

### Windows Issues

The `windows-curses` package is automatically installed on Windows. If you encounter issues:

```bash
pip install --upgrade windows-curses
```

### Terminal Size

Minimum terminal size: **80 columns × 24 rows**

Check your terminal size and resize if needed.

### Color Support

Most modern terminals support colors. If colors don't appear:

- Ensure your terminal emulator supports ANSI colors
- Try a different terminal (Windows Terminal, iTerm2, GNOME Terminal, etc.)

### Python Version

Make sure you're using Python 3.8 or higher:

```bash
python --version
```

## 💡 Tips

- **Full Screen**: Press `F11` in most terminals for fullscreen mode
- **Better Experience**: Use a larger terminal window for more entities
- **Dark Theme**: Works best with dark terminal backgrounds
- **Font**: Use a monospace font for best ASCII art rendering

## 📜 License

**GPL-3.0-or-later**

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

## 🙏 Credits

### Original Asciiquarium

- **Author**: Kirk Baucom
- **Website**: http://robobunny.com/projects/asciiquarium
- **Language**: Perl

### Python Port

- **Author**: Mohammad Abu Mattar
- **Email**: info@mkabumattar.com
- **Website**: https://mkabumattar.com/
- **Repository**: https://github.com/MKAbuMattar/asciiquarium-python

All ASCII art designs and animation concepts are credited to the original author, Kirk Baucom. This Python port maintains the spirit and fun of the original while providing modern cross-platform compatibility.

## 🔗 Links

- 📦 [PyPI Package](https://pypi.org/project/asciiquarium/)
- 🐙 [GitHub Repository](https://github.com/MKAbuMattar/asciiquarium-python)
- 🌐 [Author Website](https://mkabumattar.com/)
- � [Original Perl Version](http://robobunny.com/projects/asciiquarium)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

Made with ❤️ by [Mohammad Abu Mattar](https://mkabumattar.com/)  
Based on the original Perl ASCIIQuarium by Kirk Baucom
