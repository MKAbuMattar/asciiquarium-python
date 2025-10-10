import sys
import time
from typing import Any, Callable, Dict, List, Optional

# Handle curses import for different Python versions and platforms
try:
    import curses
except ImportError:
    # On Windows with Python 3.13+, curses might not be available
    # This will be caught and handled gracefully
    if sys.platform == "win32":
        try:
            import windows_curses as curses  # type: ignore
        except ImportError:
            raise ImportError(
                "Curses support is not available. On Windows with Python 3.13+, "
                "you may need to install windows-curses manually or use Python 3.12 or earlier."
            )
    else:
        raise

from .entity import Entity

# Z-depth constants matching the original Perl version exactly
DEPTH = {
    'gui_text': 0,
    'gui': 1,
    'shark': 2,
    'fish_start': 3,
    'fish_end': 20,
    'seaweed': 21,
    'castle': 22,
    'water_line3': 2,
    'water_gap3': 3,
    'water_line2': 4,
    'water_gap2': 5,
    'water_line1': 6,
    'water_gap1': 7,
    'water_line0': 8,
    'water_gap0': 9,
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
            # Add numbered color mappings for fish
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
        # Use halfdelay like the original for precise timing
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

            # More forgiving minimum size requirements (original was very strict)
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
        # Sort by Z-depth (lower Z values are drawn on top, like the original)
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

                # Skip transparent characters
                if entity.auto_trans and char in [" ", entity.transparent]:
                    continue
                
                # Skip empty or problematic characters
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
                    # Ensure we're drawing a valid printable character
                    char_code = ord(char)
                    if 32 <= char_code <= 126:  # Standard ASCII printable characters
                        self.screen.addch(draw_y, draw_x, char, color_attr)  # type: ignore[union-attr]
                    elif char_code > 126:  # Extended ASCII or Unicode
                        # Try to draw extended characters, fallback to space if it fails
                        try:
                            self.screen.addch(draw_y, draw_x, char, color_attr)  # type: ignore[union-attr]
                        except (curses.error, UnicodeEncodeError):
                            self.screen.addch(draw_y, draw_x, ' ', color_attr)  # type: ignore[union-attr]
                except (curses.error, ValueError, TypeError, OverflowError, UnicodeEncodeError):
                    # Skip characters that can't be drawn
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

        # Update all entities
        for entity in self.entities[:]:
            entity.update(self)

        # Check collisions
        self._check_collisions()

        # Remove dead entities
        for entity in self.entities[:]:
            if entity.should_die(self.screen_width, self.screen_height, current_time):
                if entity.death_cb:
                    entity.death_cb(entity, self)
                self.del_entity(entity)

        # Draw everything
        try:
            self.screen.erase()  # Use erase like the original
            
            # Sort entities by depth before drawing (higher Z = background, lower Z = foreground)
            sorted_entities = sorted(self.entities, key=lambda e: e.z, reverse=True)
            
            for entity in sorted_entities:
                self._draw_entity(entity)
                
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
                                paused = not paused
                            elif key == curses.KEY_RESIZE:
                                self.update_term_size()
                                self.redraw_screen()
                    except Exception:
                        pass

                    if not paused:
                        self.animate()

                    # No sleep needed - halfdelay(1) handles timing like the original
            except KeyboardInterrupt:
                self.running = False

        try:
            curses.wrapper(_run)
        except KeyboardInterrupt:
            pass
