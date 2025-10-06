from typing import Any, Callable, List, Optional, Tuple, Union


class Entity:
    """Base class for all animated entities in the aquarium"""

    def __init__(
        self,
        name: str = "",
        entity_type: str = "generic",
        shape: Union[str, List[str]] = "",
        color: Union[str, List[str]] = "",
        position: Optional[List[int]] = None,
        callback: Optional[Callable] = None,
        callback_args: Optional[List[float]] = None,
        die_time: Optional[float] = None,
        die_offscreen: bool = False,
        die_frame: Optional[int] = None,
        death_cb: Optional[Callable] = None,
        default_color: str = "WHITE",
        physical: bool = False,
        coll_handler: Optional[Callable] = None,
        auto_trans: bool = False,
        depth: int = 0,
    ):
        self.name = name
        self.entity_type = entity_type
        self.default_color = default_color
        self.physical = physical
        self.coll_handler = coll_handler
        self.auto_trans = auto_trans
        self.depth_value = depth

        if isinstance(shape, str):
            self.shapes = [shape]
        else:
            self.shapes = shape if shape else [""]

        if isinstance(color, str):
            self.colors = [color] if color else [""]
        else:
            self.colors = color if color else [""]

        # Initialize position coordinates with explicit types
        self.x: float
        self.y: float
        self.z: float
        if position is None:
            self.x, self.y, self.z = 0, 0, 0
        else:
            self.x = position[0] if len(position) > 0 else 0
            self.y = position[1] if len(position) > 1 else 0
            self.z = position[2] if len(position) > 2 else 0

        self.callback = callback
        # Initialize callback_args with explicit type
        self.callback_args: List[float]
        if callback_args is None:
            self.callback_args = [0, 0, 0, 0.5]
        else:
            self.callback_args = callback_args

        self.die_time = die_time
        self.die_offscreen = die_offscreen
        self.die_frame = die_frame
        self.death_cb = death_cb
        self.is_alive = True

        self.current_frame: int = 0
        self.frame_time: float = 0.0
        self.frame_count: int = 0

        self.collision_list: List["Entity"] = []

        self._update_dimensions()

    def _update_dimensions(self):
        """Calculate width and height from current shape"""
        if self.shapes and self.shapes[0]:
            lines = self.shapes[0].split("\n")
            self.height = len(lines)
            self.width = max(len(line) for line in lines) if lines else 0
        else:
            self.height = 0
            self.width = 0

    def get_current_shape(self) -> str:
        """Get the current animation frame's shape"""
        if not self.shapes:
            return ""
        frame_index = int(self.current_frame) % len(self.shapes)
        return self.shapes[frame_index]

    def get_current_color(self) -> str:
        """Get the current animation frame's color mask"""
        if not self.colors or not self.colors[0]:
            return ""
        frame_index = int(self.current_frame) % len(self.colors)
        return self.colors[frame_index]

    def move_entity(self, anim: Any) -> bool:
        """Move entity based on callback_args [dx, dy, dz, frame_speed]"""
        if len(self.callback_args) >= 3:
            self.x += self.callback_args[0]
            self.y += self.callback_args[1]
            self.z += self.callback_args[2]

        if len(self.callback_args) >= 4:
            self.frame_time += self.callback_args[3]
            if self.frame_time >= 1.0:
                self.current_frame += 1
                self.frame_time = 0
                self.frame_count += 1

        return True

    def position(self) -> Tuple[int, int, int]:
        """Get entity position"""
        return (int(self.x), int(self.y), int(self.z))

    def size(self) -> Tuple[int, int]:
        """Get entity dimensions"""
        return (self.width, self.height)

    def type(self) -> str:
        """Get entity type"""
        return self.entity_type

    def collisions(self) -> List["Entity"]:
        """Get list of entities this one is colliding with"""
        return self.collision_list

    def kill(self):
        """Mark entity for removal"""
        self.is_alive = False

    def should_die(
        self, screen_width: int, screen_height: int, current_time: float
    ) -> bool:
        """Check if entity should be removed"""
        if not self.is_alive:
            return True

        if self.die_time and current_time >= self.die_time:
            return True

        if self.die_frame and self.frame_count >= self.die_frame:
            return True

        if self.die_offscreen:
            if (
                self.x + self.width < 0
                or self.x >= screen_width
                or self.y + self.height < 0
                or self.y >= screen_height
            ):
                return True

        return False

    def update(self, anim: Any):
        """Update entity state (movement, animation, collision)"""
        if self.callback:
            self.callback(self, anim)
        else:
            self.move_entity(anim)

        if self.coll_handler and self.collision_list:
            self.coll_handler(self, anim)
