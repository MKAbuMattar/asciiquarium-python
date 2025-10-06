import random
import time
from typing import Any, Optional

from ..entity import Entity


def add_environment(anim: Any):
    """Add water line segments"""
    water_segments = [
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
        "^^^^ ^^^  ^^^   ^^^    ^^^^      ",
        "^^^^      ^^^^     ^^^    ^^     ",
        "^^      ^^^^      ^^^    ^^^^^^  ",
    ]

    segment_size = len(water_segments[0])
    segment_repeat = (anim.width() // segment_size) + 1

    for i, segment in enumerate(water_segments):
        tiled_segment = segment * segment_repeat
        anim.new_entity(
            name=f"water_seg_{i}",
            entity_type="waterline",
            shape=tiled_segment,
            position=[0, i + 5, 8 - i * 2],
            default_color="BLUE",
            physical=True,
        )


def add_castle(anim: Any):
    """Add castle decoration"""
    castle_shape = """
               T~~
               |
              /^\\
             /   \\
 _   _   _  /     \\  _   _   _
[ ]_[ ]_[ ]/ _   _ \\[ ]_[ ]_[ ]
|_=__-_ =_|_[ ]_[ ]_|_=-___-__|
 | _- =  | =_ = _    |= _=   |
 |= -[]  |- = _ =    |_-=_[] |
 | =_    |= - ___    | =_ =  |
 |=  []- |-  /| |\\   |=_ =[] |
 |- =_   | =| | | |  |- = -  |
 |_______|__|_|_|_|__|_______|"""

    castle_color = """
                RR
                W
              Wyyw
             y   y
 W   W   W  yWWWWWy  W   W   W
WW WW WW WW W   W WwWW WW WW WW
WWWWWWW WWWWW W W WWWWWWWWWWWWWW
 W W W  W W W W W    W  W   W
 W  W   W  W W W     W W W  W
 W  W   W  W WWW     W W W  W
 W  W   W  W W W W   W  W   W
 W  W   W W W W W W  W  W   W
 WWWWWWWWWWWWWWWWWWWWWWWWWWWWW"""

    castle_x = anim.width() - 32
    castle_y = anim.height() - 13

    anim.new_entity(
        name="castle",
        shape=castle_shape,
        color=castle_color,
        position=[castle_x, castle_y, 22],
        default_color="YELLOW",
    )


def add_seaweed(old_seaweed: Optional[Entity], anim: Any):
    """Add a seaweed plant"""
    frames = ["", ""]
    height = random.randint(3, 6)

    for i in range(1, height + 1):
        left_side = i % 2
        right_side = 1 - left_side
        frames[left_side] += "(\n"
        frames[right_side] += " )\n"

    max_x = max(1, anim.width() - 2)
    x = random.randint(1, max_x) if max_x > 1 else 1

    y = max(9, anim.height() - height)
    anim_speed = random.uniform(0.25, 0.30)

    lifetime = random.randint(8 * 60, 12 * 60)

    anim.new_entity(
        name=f"seaweed_{random.random()}",
        shape=frames,
        position=[x, y, 21],
        callback_args=[0, 0, 0, anim_speed],
        die_time=time.time() + lifetime,
        death_cb=add_seaweed,
        default_color="GREEN",
    )


def add_all_seaweed(anim: Any):
    """Add initial seaweed population"""
    seaweed_count = anim.width() // 15

    for _ in range(seaweed_count):
        add_seaweed(None, anim)
