"""Feeding logic, exercised without a terminal.

Everything here is pure geometry over Entity, so none of it needs curses. The
draw loop is the only part that does, and it is not what breaks.
"""

from asciiquarium.animation import WATER_LINE_BOTTOM
from asciiquarium.entities.fish import (
    FOOD_RANGE,
    chase_food,
    food_at_mouth,
    mouth_position,
    nearest_food,
)
from asciiquarium.entity import Entity


class FakeAnim:
    """Just enough Animation for the feeding helpers."""

    def __init__(self, entities=(), height=24, width=80):
        self.entities = list(entities)
        self._height = height
        self._width = width

    def get_entities_of_type(self, entity_type):
        return [e for e in self.entities if e.entity_type == entity_type]

    def height(self):
        return self._height

    def width(self):
        return self._width


def make_fish(x=10, y=12, speed=1.0):
    fish = Entity(entity_type="fish", shape="><>", callback_args=[speed, 0, 0])
    fish.x, fish.y = x, y
    return fish


def make_food(x, y):
    food = Entity(entity_type="food", shape="#", callback_args=[0, 0.15, 0, 0])
    food.x, food.y = x, y
    return food


def test_ignores_food_beyond_range():
    fish = make_fish(x=0)
    far = make_food(x=FOOD_RANGE + 50, y=12)
    assert nearest_food(fish, FakeAnim([far])) is None


def test_prefers_food_ahead_over_equidistant_food_behind():
    fish = make_fish(x=20, speed=1.0)  # swimming right
    ahead = make_food(x=28, y=12)
    behind = make_food(x=13, y=12)

    assert nearest_food(fish, FakeAnim([behind, ahead])) is ahead


def test_direction_is_read_from_speed_not_position():
    fish = make_fish(x=20, speed=-1.0)  # swimming left
    left = make_food(x=13, y=12)
    right = make_food(x=28, y=12)

    assert nearest_food(fish, FakeAnim([right, left])) is left


def test_chasing_never_sinks_a_fish_off_the_bottom():
    """The bug this clamp exists for: feeding fish used to delete them.

    Entity.should_die culls anything with y >= screen height, so an unclamped
    fish following a flake to the floor swims out of existence.
    """
    anim = FakeAnim(height=24)
    fish = make_fish(y=WATER_LINE_BOTTOM)
    below = make_food(x=12, y=anim.height() + 5)

    for _ in range(200):
        chase_food(fish, below, anim)

    assert fish.y > WATER_LINE_BOTTOM, "fish should have descended toward the food"
    assert fish.y < anim.height(), "fish sank past the cull threshold"


def test_chasing_never_rises_through_the_waterline():
    anim = FakeAnim()
    fish = make_fish(y=WATER_LINE_BOTTOM)
    above = make_food(x=12, y=0)

    for _ in range(200):
        chase_food(fish, above, anim)

    assert fish.y >= WATER_LINE_BOTTOM


def test_chasing_leaves_speed_and_direction_untouched():
    """Boosts must not accumulate into callback_args, or fish ratchet up forever."""
    anim = FakeAnim()
    fish = make_fish(speed=1.0)
    food = make_food(x=25, y=12)

    for _ in range(50):
        chase_food(fish, food, anim)

    assert fish.callback_args == [1.0, 0, 0]


def test_food_must_reach_the_mouth_not_just_the_body():
    fish = make_fish(x=10, y=12, speed=1.0)  # occupies x 10..12, mouth at 12
    fish_x, fish_y, _ = fish.position()

    assert food_at_mouth(fish, make_food(*mouth_position(fish)))
    assert not food_at_mouth(fish, make_food(fish_x - 6, fish_y))


def test_mouth_is_at_the_leading_edge_for_both_directions():
    fish_w = make_fish(x=10, speed=1.0).size()[0]

    rightward = mouth_position(make_fish(x=10, speed=1.0))[0]
    leftward = mouth_position(make_fish(x=10, speed=-1.0))[0]

    assert rightward == 10 + fish_w - 1
    assert leftward == 10


def test_food_stops_spawning_at_the_cap():
    from asciiquarium.entities.food import MAX_FOOD, add_food

    anim = FakeAnim()
    anim.new_entity = lambda **kw: _append(anim, kw)

    for _ in range(MAX_FOOD + 5):
        add_food(None, anim)

    assert len(anim.get_entities_of_type("food")) == MAX_FOOD


def _append(anim, kwargs):
    entity = Entity(**kwargs)
    anim.entities.append(entity)
    return entity
