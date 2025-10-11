import sys
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import curses
except ImportError:
    if sys.platform == "win32":
        try:
            import windows_curses as curses
        except ImportError:
            raise ImportError(
                "Curses support is not available. On Windows with Python 3.13+, "
                "you may need to install windows-curses manually or use Python 3.12 or earlier."
            )
    else:
        raise

from .__version__ import (
    __author__,
    __email__,
    __license__,
    __original_author__,
    __original_project__,
    __version__,
)
from .entity import Entity

DEPTH = {
    "gui_text": 0,
    "gui": 1,
    "shark": 2,
    "fish_start": 3,
    "fish_end": 20,
    "seaweed": 21,
    "castle": 22,
    "water_line3": 2,
    "water_gap3": 3,
    "water_line2": 4,
    "water_gap2": 5,
    "water_line1": 6,
    "water_gap1": 7,
    "water_line0": 8,
    "water_gap0": 9,
}


class Animation:
    """Main animation controller that manages the screen and all entities"""

    def __init__(self) -> None:
        self.screen: Optional[Any] = None
        self.entities: List[Entity] = []
        self.color_enabled = True
        self.running = False
        self.screen_width: int = 0
        self.screen_height: int = 0
        self.color_pairs: Dict[str, int] = {}
        self._init_color_pairs()

    def _init_color_pairs(self) -> None:
        """Initialize color pair mappings"""
        self.color_map = {
            "BLACK": curses.COLOR_BLACK,
            "RED": curses.COLOR_RED,
            "GREEN": curses.COLOR_GREEN,
            "YELLOW": curses.COLOR_YELLOW,
            "BLUE": curses.COLOR_BLUE,
            "MAGENTA": curses.COLOR_MAGENTA,
            "CYAN": curses.COLOR_CYAN,
            "WHITE": curses.COLOR_WHITE,
        }

        self.mask_color_map = {
            "r": "RED",
            "R": "RED",
            "g": "GREEN",
            "G": "GREEN",
            "y": "YELLOW",
            "Y": "YELLOW",
            "b": "BLUE",
            "B": "BLUE",
            "m": "MAGENTA",
            "M": "MAGENTA",
            "c": "CYAN",
            "C": "CYAN",
            "w": "WHITE",
            "W": "WHITE",
            "k": "BLACK",
            "K": "BLACK",
            "1": "CYAN",
            "2": "YELLOW",
            "3": "GREEN",
            "4": "WHITE",
            "5": "RED",
            "6": "BLUE",
            "7": "MAGENTA",
            "8": "BLACK",
            "9": "WHITE",
        }

    def init_screen(self, stdscr):
        """Initialize the curses screen"""
        self.screen = stdscr
        curses.halfdelay(1)
        self.screen.keypad(1)
        curses.curs_set(0)

        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

        pair_id = 1
        for fg_name, fg_code in self.color_map.items():
            try:
                curses.init_pair(pair_id, fg_code, -1)
                self.color_pairs[fg_name] = pair_id
                pair_id += 1
            except curses.error:
                pass
        self.update_term_size()

    def update_term_size(self) -> None:
        """Update terminal dimensions"""
        if self.screen:
            raw_height, self.screen_width = self.screen.getmaxyx()
            self.screen_height = raw_height - 1

            if raw_height < 15 or self.screen_width < 40:
                raise ValueError(
                    f"Terminal too small! Need at least 40x15, got {self.screen_width}x{raw_height}.\n"
                    "Please resize your terminal and try again."
                )

    def width(self) -> int:
        """Get screen width"""
        return self.screen_width

    def height(self) -> int:
        """Get screen height"""
        return self.screen_height

    def color(self, enabled: bool):
        """Enable or disable color"""
        self.color_enabled = enabled

    def new_entity(self, **kwargs) -> Entity:
        """Create and add a new entity"""
        entity = Entity(**kwargs)
        self.add_entity(entity)
        return entity

    def add_entity(self, entity: Entity):
        """Add an existing entity"""
        self.entities.append(entity)
        self.entities.sort(key=lambda e: e.z)

    def del_entity(self, entity: Entity):
        """Remove an entity"""
        if entity in self.entities:
            self.entities.remove(entity)

    def remove_all_entities(self):
        """Clear all entities"""
        self.entities.clear()

    def get_entities_of_type(self, entity_type: str) -> List[Entity]:
        """Get all entities of a specific type"""
        return [e for e in self.entities if e.entity_type == entity_type]

    def _check_collisions(self):
        """Check for collisions between physical entities"""
        physical_entities = [e for e in self.entities if e.physical]

        for entity in physical_entities:
            entity.collision_list.clear()

            for other in self.entities:
                if entity is other:
                    continue

                e_x, e_y, _ = entity.position()
                e_w, e_h = entity.size()
                o_x, o_y, _ = other.position()
                o_w, o_h = other.size()

                if (
                    e_x < o_x + o_w
                    and e_x + e_w > o_x
                    and e_y < o_y + o_h
                    and e_y + e_h > o_y
                ):
                    entity.collision_list.append(other)

    def _draw_entity(self, entity: Entity):
        """Draw a single entity to the screen"""
        shape = entity.get_current_shape()
        color_mask = entity.get_current_color()
        x, y, _ = entity.position()

        lines = shape.split("\n")
        color_lines = color_mask.split("\n") if color_mask else []

        for line_idx, line in enumerate(lines):
            draw_y = y + line_idx
            if draw_y < 0 or draw_y >= self.screen_height:
                continue

            color_line = color_lines[line_idx] if line_idx < len(color_lines) else ""

            for char_idx, char in enumerate(line):
                draw_x = x + char_idx
                if draw_x < 0 or draw_x >= self.screen_width:
                    continue

                if entity.auto_trans and char in [" ", entity.transparent]:
                    continue

                if char in ["\r", "\n", "\t"] or ord(char) < 32:
                    continue

                color_attr = 0
                if self.color_enabled and char_idx < len(color_line):
                    color_char = color_line[char_idx]
                    if color_char in self.mask_color_map:
                        color_name = self.mask_color_map[color_char]
                        if color_name in self.color_pairs:
                            color_attr = curses.color_pair(self.color_pairs[color_name])

                if color_attr == 0 and entity.default_color in self.color_pairs:
                    color_attr = curses.color_pair(
                        self.color_pairs[entity.default_color]
                    )

                try:
                    char_code = ord(char)
                    if 32 <= char_code <= 126:
                        self.screen.addch(draw_y, draw_x, char, color_attr)
                    elif char_code > 126:
                        try:
                            self.screen.addch(draw_y, draw_x, char, color_attr)
                        except (curses.error, UnicodeEncodeError):
                            self.screen.addch(draw_y, draw_x, " ", color_attr)
                except (
                    curses.error,
                    ValueError,
                    TypeError,
                    OverflowError,
                    UnicodeEncodeError,
                ):
                    pass

    def redraw_screen(self):
        """Clear and redraw the entire screen"""
        if not self.screen:
            return

        try:
            self.screen.clear()
        except curses.error:
            pass

    def animate(self):
        """Update all entities and redraw the screen"""
        if not self.screen:
            return

        current_time = time.time()

        for entity in self.entities[:]:
            entity.update(self)

        self._check_collisions()

        for entity in self.entities[:]:
            if entity.should_die(self.screen_width, self.screen_height, current_time):
                if entity.death_cb:
                    entity.death_cb(entity, self)
                self.del_entity(entity)

        try:
            self.screen.erase()

            sorted_entities = sorted(self.entities, key=lambda e: e.z, reverse=True)

            for entity in sorted_entities:
                self._draw_entity(entity)

            self.screen.refresh()
        except curses.error:
            pass

    def show_info_overlay(self):
        """Display info overlay on top of paused animation"""
        try:
            height, width = self.screen.getmaxyx()

            for y in range(height):
                try:
                    self.screen.addstr(y, 0, " " * (width - 1))
                except curses.error:
                    pass

            info_lines = [
                "╔═══════════════════════════════════════════════════════════════════════╗",
                "║                                                                       ║",
                f"║   🐠 Asciiquarium {__version__} - ASCII Art Aquarium Animation                ║",
                "║                                                                       ║",
                "╚═══════════════════════════════════════════════════════════════════════╝",
                "",
                "  An aquarium/sea animation in ASCII art for your terminal!",
                "",
                "  FEATURES:",
                "    • Multiple fish species with different sizes and colors",
                "    • Sharks that hunt small fish",
                "    • Whales with animated water spouts",
                "    • Ships sailing on the surface",
                "    • Sea monsters lurking in the depths",
                "    • Animated blue water lines and seaweed",
                "    • Castle decoration",
                "    • Blue bubbles rising from fish",
                "",
                "  CONTROLS:",
                "    Q or q  - Quit the aquarium",
                "    P or p  - Pause/unpause animation",
                "    R or r  - Redraw and respawn entities",
                "    I or i  - Show/hide this info screen",
                "",
                "  CREDITS:",
                f"    Python Port     : {__author__} <{__email__}>",
                f"    Original Author : {__original_author__}",
                f"    Original Project: {__original_project__}",
                "",
                "  LICENSE: " + __license__,
                "",
                "  Press 'I' or ESC to return to aquarium...",
            ]

            start_y = max(0, (height - len(info_lines)) // 2)

            for i, line in enumerate(info_lines):
                y = start_y + i
                if y < height - 1:
                    x = max(0, (width - len(line)) // 2)
                    try:
                        self.screen.addstr(y, x, line[: width - 1])
                    except curses.error:
                        pass

            self.screen.refresh()

        except curses.error:
            pass

    def run(self, setup_callback: Callable):
        """Main animation loop"""

        def _run(stdscr):
            self.init_screen(stdscr)
            self.running = True

            setup_callback(self)

            paused = False
            showing_info = False
            last_time = time.time()

            try:
                while self.running:
                    try:
                        key = self.screen.getch()
                        if key != -1:
                            key_char = chr(key).lower() if key < 256 else ""

                            if key_char == "q":
                                self.running = False
                            elif key_char == "r":
                                self.remove_all_entities()
                                setup_callback(self)
                                self.redraw_screen()
                            elif key_char == "p":
                                if not showing_info:
                                    paused = not paused
                            elif key_char == "i":
                                showing_info = not showing_info
                                if showing_info:
                                    paused = True
                                    self.show_info_overlay()
                                else:
                                    paused = False
                                    self.redraw_screen()
                            elif key == 27:
                                if showing_info:
                                    showing_info = False
                                    paused = False
                                    self.redraw_screen()
                            elif key == curses.KEY_RESIZE:
                                self.update_term_size()
                                if showing_info:
                                    self.show_info_overlay()
                                else:
                                    self.redraw_screen()
                    except Exception:
                        pass

                    if not paused and not showing_info:
                        self.animate()
                    elif showing_info:
                        pass

            except KeyboardInterrupt:
                self.running = False

        try:
            curses.wrapper(_run)
        except KeyboardInterrupt:
            pass
