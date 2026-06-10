"""Food entity for the aquarium."""

import random
from typing import Any, Optional

from ..animation import DEPTH
from ..entity import Entity

MAX_FOOD = 5


def add_food(old_food: Optional[Entity], anim: Any) -> Optional[Entity]:
    """Add a single food pellet to the aquarium.

    Food is represented by a single '#' character.
    It starts near the top of the water and slowly sinks.
    """
    existing_food = anim.get_entities_of_type("food")
    if len(existing_food) >= MAX_FOOD:
        return None

    x = random.randint(1, max(1, anim.width() - 2))
    y = 6  # just below the animated water lines

    return anim.new_entity(
        name=f"food_{random.random()}",
        entity_type="food",
        shape="#",
        position=[x, y, DEPTH["fish_start"] - 1],
        callback_args=[random.uniform(-0.05, 0.05), 0.15, 0, 0],
        die_offscreen=True,
        physical=True,
        default_color="YELLOW",
    )