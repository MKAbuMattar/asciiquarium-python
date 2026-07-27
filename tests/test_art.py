"""Invariants the ASCII art has to hold, checked without a terminal.

Art breaks silently in this codebase: a mask that no longer lines up with its
shape still renders, just in the wrong colours. Nothing here can tell whether
a fish looks right — only that the pairs are still structurally sound and that
every colour name reaches a real curses colour pair.
"""

import random

import pytest
from fake_anim import FakeAnim

from asciiquarium.animation import Animation
from asciiquarium.entities import add_all_fish, add_all_seaweed, add_castle, add_environment
from asciiquarium.entities.fish import FISH_DESIGNS, rand_color
from asciiquarium.entities.special import RANDOM_OBJECTS
from asciiquarium.entity import Entity


def populated_anim(classic_mode: bool = False, seed: int = 0) -> FakeAnim:
    """One of every creature the aquarium can put on screen."""
    random.seed(seed)
    anim = FakeAnim(height=50, width=200)
    add_environment(anim)
    add_castle(anim)
    add_all_seaweed(anim)
    add_all_fish(anim, classic_mode)
    for spawn in RANDOM_OBJECTS:
        spawn(None, anim)
    return anim


@pytest.mark.parametrize("index", range(len(FISH_DESIGNS)))
def test_fish_design_has_a_mask_for_every_frame(index):
    design = FISH_DESIGNS[index]
    assert len(design["shape"]) == len(design["color"])


@pytest.mark.parametrize("index", range(len(FISH_DESIGNS)))
def test_fish_mask_covers_every_row_of_its_shape(index):
    """A mask with fewer lines than its shape leaves whole rows uncoloured."""
    design = FISH_DESIGNS[index]
    for frame, (shape, mask) in enumerate(zip(design["shape"], design["color"])):
        shape_rows = len(shape.split("\n"))
        mask_rows = len(mask.split("\n"))
        assert mask_rows >= shape_rows, f"design {index} frame {frame}"


@pytest.mark.parametrize("index", range(len(FISH_DESIGNS)))
def test_no_placeholder_digit_survives_rand_color(index):
    """1-9 are placeholders. One reaching the renderer is a bug in the mask."""
    for mask in FISH_DESIGNS[index]["color"]:
        for seed in range(20):
            random.seed(seed)
            assert not any(char.isdigit() for char in rand_color(mask))


@pytest.mark.parametrize("classic_mode", [False, True])
def test_every_default_color_is_a_real_color(classic_mode):
    """`default_color="blue"` does not raise — it renders with no colour at all.

    Animation builds its pair table from the uppercase names in color_map, so a
    name that is not a key there silently loses its colour.
    """
    known = set(Animation().color_map)

    for entity in populated_anim(classic_mode).entities:
        assert entity.default_color in known, f"{entity.name or entity.entity_type}"


def test_multi_frame_entity_is_measured_across_all_frames():
    """size() feeds collision and the offscreen cull, not just the first frame.

    The whale, the sea monsters and the ducks all have frames of differing
    widths; measuring shapes[0] culls and collides them against a stale box.
    """
    wide_second_frame = Entity(shape=["ab", "abcdef"])
    tall_second_frame = Entity(shape=["a", "a\nb\nc"])

    assert wide_second_frame.size() == (6, 1)
    assert tall_second_frame.size() == (1, 3)


def test_empty_entity_has_no_size():
    assert Entity().size() == (0, 0)
