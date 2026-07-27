import random
from typing import Any, Optional

from ..animation import DEPTH, WATER_LINE_BOTTOM
from ..entity import Entity

MAX_FOOD = 10
FOOD_SINK_SPEED = 0.15
FOOD_DRIFT = 0.05


def add_food(old_food: Optional[Entity], anim: Any) -> Optional[Entity]:
    """Drop one flake of food just under the waterline.

    Returns None once MAX_FOOD flakes are already falling, so holding the key
    down cannot fill the tank.
    """
    if len(anim.get_entities_of_type("food")) >= MAX_FOOD:
        return None

    flake: Entity = anim.new_entity(
        entity_type="food",
        shape="#",
        position=[
            random.randint(1, max(1, anim.width() - 2)),
            WATER_LINE_BOTTOM,
            DEPTH["fish_start"] - 1,
        ],
        callback_args=[random.uniform(-FOOD_DRIFT, FOOD_DRIFT), FOOD_SINK_SPEED, 0, 0],
        die_offscreen=True,
        physical=True,
        default_color="YELLOW",
    )
    return flake
