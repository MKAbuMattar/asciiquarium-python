import random
import time
from typing import Any, Optional, Tuple

from ..animation import DEPTH
from ..entity import Entity


def add_bubble(fish: Entity, anim: Any):
    """Add an air bubble from a fish"""
    cb_args = fish.callback_args
    fish_w, fish_h = fish.size()
    fish_x, fish_y, fish_z = fish.position()

    bubble_x = fish_x
    bubble_y = fish_y + fish_h // 2
    bubble_z = fish_z - 1

    if isinstance(cb_args, list) and cb_args[0] > 0:
        bubble_x += fish_w

    anim.new_entity(
        entity_type="bubble",
        shape=[".", "o", "O", "O", "O"],
        position=[bubble_x, bubble_y, bubble_z],
        callback_args=[0, -1, 0, 0.1],
        die_offscreen=True,
        physical=True,
        coll_handler=bubble_collision,
        default_color="CYAN",
    )


def bubble_collision(bubble: Entity, anim: Any):
    """Handle bubble collision with waterline"""
    for col_obj in bubble.collisions():
        if col_obj.entity_type == "waterline":
            bubble.kill()
            break


FOOD_DETECTION_RANGE = 30
FOOD_VERTICAL_SPEED = 0.25
FOOD_CHASE_BOOST = 0.30
HAPPY_FISH_BUBBLE_THRESHOLD = 90
HAPPY_FISH_V3_SMALL_SPEED_BOOST = 0.55
HAPPY_FISH_V3_MEDIUM_SPEED_BOOST = 0.38
HAPPY_FISH_V3_LARGE_SPEED_BOOST = 0.20
HAPPY_FISH_V3_DANCE_VERTICAL_SPEED = 0.45
HAPPY_FISH_V3_DANCE_PERIOD = 20
HAPPY_FISH_V3_BUBBLE_BURST_COUNT = 4
HAPPY_FISH_V3_SPARKLE_CHANCE_PERCENT = 35
HAPPY_FISH_V3_SPARKLE_COLORS = ["YELLOW", "MAGENTA", "CYAN", "WHITE"]
HAPPY_FISH_V4_RAINBOW_COLORS = ["RED", "YELLOW", "GREEN", "CYAN", "BLUE", "MAGENTA", "WHITE"]
HAPPY_FISH_V4_RAINBOW_FRAME_STEP = 2
HAPPY_FISH_BUBBLE_BURST_COUNT = 4
HAPPY_FISH_SMALL_SPEED_BOOST = 0.45
HAPPY_FISH_MEDIUM_SPEED_BOOST = 0.30
HAPPY_FISH_LARGE_SPEED_BOOST = 0.15
HAPPY_FISH_WIGGLE_SPEED = 0.20
HAPPY_FISH_WIGGLE_PERIOD = 6


def find_nearest_food(fish: Entity, anim: Any) -> Optional[Entity]:
    """Find the best food flake for this fish to chase.

    Fish strongly prefer food in front of them, but they may still notice
    food behind them if it is very close.
    """
    foods = anim.get_entities_of_type("food")
    if not foods:
        return None

    fish_x, fish_y, _ = fish.position()
    fish_w, fish_h = fish.size()
    fish_center_x = fish_x + fish_w // 2
    fish_center_y = fish_y + fish_h // 2

    base_dx = getattr(fish, "base_dx", None)
    if base_dx is None and isinstance(fish.callback_args, list) and fish.callback_args:
        base_dx = fish.callback_args[0]

    swimming_right = True if base_dx is None else base_dx > 0

    nearest_food = None
    best_score = FOOD_DETECTION_RANGE + 1

    for food in foods:
        food_x, food_y, _ = food.position()

        horizontal_distance = abs(food_x - fish_center_x)
        vertical_distance = abs(food_y - fish_center_y)
        distance = horizontal_distance + vertical_distance

        food_is_ahead = (
            swimming_right and food_x >= fish_center_x
        ) or (
            not swimming_right and food_x <= fish_center_x
        )

        # Ignore food outside normal detection range.
        if distance > FOOD_DETECTION_RANGE:
            continue

        if food_is_ahead:
            # Food in front is attractive.
            score = distance
        else:
            # Food behind the fish is much less attractive.
            # Only chase it if it is quite close.
            if distance > FOOD_DETECTION_RANGE // 3:
                continue

            score = distance + 15

        if score < best_score:
            best_score = score
            nearest_food = food

    return nearest_food


def fish_mouth_position(fish: Entity) -> Tuple[int, int]:
    """Return the approximate mouth position of a fish.

    The mouth is assumed to be vertically centered on the fish and at the
    front edge of the fish, based on the fish's swimming direction.
    """
    fish_x, fish_y, _ = fish.position()
    fish_w, fish_h = fish.size()

    mouth_y = fish_y + fish_h // 2

    # Prefer the original speed/direction if we stored it when creating the fish.
    # This avoids a temporarily boosted food-chase speed confusing the direction.
    base_dx = getattr(fish, "base_dx", None)
    if base_dx is None and isinstance(fish.callback_args, list) and fish.callback_args:
        base_dx = fish.callback_args[0]

    swimming_right = True if base_dx is None else base_dx > 0
    mouth_x = fish_x + fish_w - 1 if swimming_right else fish_x

    return mouth_x, mouth_y


def food_touches_fish_mouth(fish: Entity, food: Entity) -> bool:
    """Return True if food touches the approximate mouth area of the fish.

    Uses a small hitbox around the estimated mouth because ASCII fish have
    irregular shapes and fractional movement is rounded to integer positions.
    """
    food_x, food_y, _ = food.position()
    mouth_x, mouth_y = fish_mouth_position(fish)

    mouth_x_tolerance = 2
    mouth_y_tolerance = 1

    return (
        abs(food_x - mouth_x) <= mouth_x_tolerance
        and abs(food_y - mouth_y) <= mouth_y_tolerance
    )


def add_food_bubble(food: Entity, anim: Any):
    """Add a bubble at the location where food was eaten."""
    food_x, food_y, food_z = food.position()

    anim.new_entity(
        entity_type="bubble",
        shape=[".", "o", "O", "O", "O"],
        position=[food_x, food_y, food_z - 1],
        callback_args=[0, -1, 0, 0.1],
        die_offscreen=True,
        physical=True,
        coll_handler=bubble_collision,
        default_color="CYAN",
    )


def happy_fish_speed_boost(fish: Entity) -> float:
    """Return a size-based Happy Fish speed boost for ordinary fish."""
    fish_w, fish_h = fish.size()
    fish_area = fish_w * fish_h

    if fish_area <= 25:
        return HAPPY_FISH_SMALL_SPEED_BOOST
    if fish_area <= 70:
        return HAPPY_FISH_MEDIUM_SPEED_BOOST
    return HAPPY_FISH_LARGE_SPEED_BOOST


def happy_fish_wiggle_dy(fish: Entity) -> float:
    """Return a subtle up/down wiggle for Happy Fish mode."""
    phase = int((time.time() * 8) + abs(fish.x) + abs(fish.y)) % HAPPY_FISH_WIGGLE_PERIOD

    if phase in (0, 1):
        return -HAPPY_FISH_WIGGLE_SPEED
    if phase in (3, 4):
        return HAPPY_FISH_WIGGLE_SPEED
    return 0.0


def add_happy_fish_bubble_burst(fish: Entity, anim: Any) -> None:
    """Emit a short one-time bubble burst from a Happy Fish."""
    for _ in range(HAPPY_FISH_BUBBLE_BURST_COUNT):
        add_bubble(fish, anim)



def happy_fish_v3_speed_boost(fish: Entity) -> float:
    # Size-based speed boost for ordinary fish. Sharks do not use this callback.
    fish_w, fish_h = fish.size()
    fish_area = fish_w * fish_h

    if fish_area <= 30:
        return HAPPY_FISH_V3_SMALL_SPEED_BOOST
    if fish_area <= 70:
        return HAPPY_FISH_V3_MEDIUM_SPEED_BOOST
    return HAPPY_FISH_V3_LARGE_SPEED_BOOST


def happy_fish_v3_dance_dy(fish: Entity, anim: Any) -> float:
    # Stronger, visible one-row-ish dance pattern.
    frame_count = getattr(anim, "frame_count", 0)
    phase = (frame_count + int(abs(fish.x) + abs(fish.y))) % HAPPY_FISH_V3_DANCE_PERIOD

    if phase < 5:
        dy = -HAPPY_FISH_V3_DANCE_VERTICAL_SPEED
    elif phase < 10:
        dy = 0
    elif phase < 15:
        dy = HAPPY_FISH_V3_DANCE_VERTICAL_SPEED
    else:
        dy = 0

    # Keep fish away from waterline and bottom decorations.
    fish_w, fish_h = fish.size()
    if dy < 0 and fish.y <= 8:
        return 0
    if dy > 0 and fish.y + fish_h >= anim.height() - 3:
        return 0
    return dy


def add_happy_fish_sparkle(fish: Entity, anim: Any) -> None:
    # Add a short-lived sparkle near the fish.
    fish_x, fish_y, fish_z = fish.position()
    fish_w, fish_h = fish.size()

    sparkle_x = fish_x + random.randint(0, max(0, fish_w - 1))
    sparkle_y = fish_y + random.randint(0, max(0, fish_h - 1))
    sparkle_z = fish_z - 1

    anim.new_entity(
        entity_type="happy_sparkle",
        shape=["*", "+", ".", " "],
        position=[sparkle_x, sparkle_y, sparkle_z],
        callback_args=[random.choice([-0.05, 0, 0.05]), -0.15, 0, 0.45],
        die_offscreen=True,
        default_color=random.choice(HAPPY_FISH_V3_SPARKLE_COLORS),
        auto_trans=True,
        die_frame=4,
    )


def add_happy_fish_bubble_burst(fish: Entity, anim: Any) -> None:
    for _ in range(HAPPY_FISH_V3_BUBBLE_BURST_COUNT):
        add_bubble(fish, anim)






def apply_happy_fish_rainbow_color(entity: Entity, anim: Any) -> None:
    # Temporarily cycle the whole fish body through bright colors.
    # Entity.get_current_color() reads entity.colors, not entity.color.
    if not hasattr(entity, "base_default_color"):
        entity.base_default_color = getattr(entity, "default_color", None)
    if not hasattr(entity, "base_colors"):
        current_colors = getattr(entity, "colors", None)
        entity.base_colors = list(current_colors) if isinstance(current_colors, list) else current_colors

    frame_count = getattr(anim, "frame_count", 0)
    phase_offset = int(abs(getattr(entity, "x", 0)) + abs(getattr(entity, "y", 0)))
    colors = HAPPY_FISH_V4_RAINBOW_COLORS
    color_index = ((frame_count // HAPPY_FISH_V4_RAINBOW_FRAME_STEP) + phase_offset) % len(colors)
    mask_chars = ["r", "y", "g", "c", "b", "m", "w"]
    mask_char = mask_chars[color_index]
    entity.default_color = colors[color_index]

    def mask_for_shape(shape_text: str) -> str:
        return chr(10).join(
            "".join(mask_char if ch != " " else " " for ch in line)
            for line in str(shape_text).split(chr(10))
        )

    shapes = getattr(entity, "shapes", None)
    if isinstance(shapes, list) and shapes:
        entity.colors = [mask_for_shape(shape) for shape in shapes]
    else:
        entity.colors = [mask_for_shape(entity.get_current_shape())]


def restore_happy_fish_base_color(entity: Entity) -> None:
    # Restore original color masks and default color after Happy Fish mode ends.
    if hasattr(entity, "base_colors"):
        base_colors = entity.base_colors
        entity.colors = list(base_colors) if isinstance(base_colors, list) else base_colors
    if hasattr(entity, "base_default_color"):
        entity.default_color = entity.base_default_color


def fish_callback(fish: Entity, anim: Any) -> bool:
    """Fish behavior - blow bubbles, dance during Happy Fish, and react to food."""
    happy_fish_active = bool(getattr(anim, "happy_fish_active", lambda: False)())

    # Do not apply Happy Fish movement boosts to sharks if a shark ever uses
    # this callback.
    if getattr(fish, "entity_type", "fish") == "shark":
        happy_fish_active = False

    if happy_fish_active and getattr(fish, "happy_fish_burst_pending", False):
        add_happy_fish_bubble_burst(fish, anim)
        fish.happy_fish_burst_pending = False
    elif not happy_fish_active:
        fish.happy_fish_burst_pending = False

    bubble_threshold = HAPPY_FISH_BUBBLE_THRESHOLD if happy_fish_active else 97
    if random.randint(1, 100) > bubble_threshold:
        add_bubble(fish, anim)

    if happy_fish_active and random.randint(1, 100) <= HAPPY_FISH_V3_SPARKLE_CHANCE_PERCENT:
        add_happy_fish_sparkle(fish, anim)

    if not isinstance(fish.callback_args, list):
        if happy_fish_active:
            apply_happy_fish_rainbow_color(fish, anim)
        else:
            restore_happy_fish_base_color(fish)
        return fish.move_entity(anim)

    # Store the fish\'s original horizontal speed once, so boosts do not
    # accumulate every frame.
    if not hasattr(fish, "base_dx"):
        fish.base_dx = fish.callback_args[0] if fish.callback_args else 0

    base_dx = fish.base_dx

    # During Happy Fish mode, ignore food so the dance is visible instead of
    # being obscured by food-chasing movement.
    nearest_food = None if happy_fish_active else find_nearest_food(fish, anim)

    if nearest_food:
        fish_x, fish_y, _ = fish.position()
        fish_w, fish_h = fish.size()
        fish_center_x = fish_x + fish_w // 2
        fish_center_y = fish_y + fish_h // 2

        food_x, food_y, _ = nearest_food.position()

        if food_y > fish_center_y:
            fish.callback_args[1] = FOOD_VERTICAL_SPEED
        elif food_y < fish_center_y:
            fish.callback_args[1] = -FOOD_VERTICAL_SPEED
        else:
            fish.callback_args[1] = 0

        swimming_right = base_dx > 0
        food_is_ahead = (
            swimming_right and food_x > fish_center_x
        ) or (
            not swimming_right and food_x < fish_center_x
        )

        if food_is_ahead:
            if swimming_right:
                fish.callback_args[0] = abs(base_dx) + FOOD_CHASE_BOOST
            else:
                fish.callback_args[0] = -abs(base_dx) - FOOD_CHASE_BOOST
        else:
            fish.callback_args[0] = base_dx
    else:
        if happy_fish_active:
            speed_boost = happy_fish_v3_speed_boost(fish)
            if base_dx > 0:
                fish.callback_args[0] = abs(base_dx) + speed_boost
            elif base_dx < 0:
                fish.callback_args[0] = -abs(base_dx) - speed_boost
            else:
                fish.callback_args[0] = base_dx
            fish.callback_args[1] = happy_fish_v3_dance_dy(fish, anim)
        else:
            fish.callback_args[0] = base_dx
            fish.callback_args[1] = 0

    if happy_fish_active:
        apply_happy_fish_rainbow_color(fish, anim)
    else:
        restore_happy_fish_base_color(fish)

    return fish.move_entity(anim)

def fish_collision(fish: Entity, anim: Any):
    """Handle fish collision with predators, fishing hook, and food."""
    from .special import retract

    for col_obj in fish.collisions():
        if col_obj.entity_type == "food":
            if food_touches_fish_mouth(fish, col_obj):
                add_munch(anim, fish)
                add_food_bubble(col_obj, anim)
                col_obj.kill()
                break

        elif col_obj.entity_type == "teeth" and fish.height <= 5:
            add_splat(anim, *col_obj.position())
            fish.kill()
            break

        elif col_obj.entity_type == "hook_point":
            retract(col_obj, anim)
            retract(fish, anim)

            hooks = anim.get_entities_of_type("fishhook")
            lines = anim.get_entities_of_type("fishline")

            if hooks:
                retract(hooks[0], anim)
            if lines:
                retract(lines[0], anim)
            break


def munch_callback(munch: Entity, anim: Any) -> bool:
    """Keep the munch animation attached to the fish's mouth.

    The munch entity may update before the fish moves during this frame,
    so this predicts the fish's next mouth position to avoid visual lag.
    """
    if not isinstance(munch.callback_args, dict):
        return munch.move_entity(anim)

    fish = munch.callback_args.get("fish")

    if fish is None or not fish.is_alive:
        munch.kill()
        return True

    mouth_x, mouth_y = fish_mouth_position(fish)
    _, _, fish_z = fish.position()

    predicted_dx = 0
    predicted_dy = 0

    if isinstance(fish.callback_args, list):
        if len(fish.callback_args) > 0:
            predicted_dx = fish.callback_args[0]
        if len(fish.callback_args) > 1:
            predicted_dy = fish.callback_args[1]

    munch.x = mouth_x + predicted_dx
    munch.y = mouth_y + predicted_dy
    munch.z = fish_z - 1

    # Advance animation frames.
    frame_speed = munch.callback_args.get("frame_speed", 0.35)
    munch.frame_time += frame_speed

    if munch.frame_time >= 1.0:
        munch.current_frame += 1
        munch.frame_time = 0.0

    munch.frame_count += 1

    return True
    

def add_munch(anim: Any, fish: Entity):
    """Create a small munch animation attached to the fish's mouth."""
    mouth_x, mouth_y = fish_mouth_position(fish)
    _, _, fish_z = fish.position()

    munch_frames = [
        "*",
        "+",
        ".",
    ]

    anim.new_entity(
        entity_type="munch",
        shape=munch_frames,
        position=[mouth_x, mouth_y, fish_z - 1],
        callback=munch_callback,
        callback_args={
            "fish": fish,
            "frame_speed": 0.35,
        },
        default_color="YELLOW",
        auto_trans=True,
        die_frame=len(munch_frames),
    )
    

def add_splat(anim: Any, x: int, y: int, z: int):
    """Create a splat animation when fish is eaten"""
    splat_frames = [
        "\n\n   .\n  ***\n   '\n\n",
        "\n\n .,*;`\n '*,**\n *'~'\n\n",
        '\n  , ,\n " ,"\'\n *" *\'"\n  " ; .\n\n',
        "* ' , ' `\n' ` * . '\n ' `' \",'\n* ' \" * .\n\" * ', '",
    ]

    anim.new_entity(
        shape=splat_frames,
        position=[x - 4, y - 2, z - 2],
        default_color="RED",
        callback_args=[0, 0, 0, 0.25],
        auto_trans=True,
        die_frame=15,
    )


OLD_FISH_DESIGNS = [
    {
        "shape": [
            "       \\\n     ...\\..,\n\\  /'       \\\n >=     (  ' >\n/  \\      / /\n    `\"'\"'/''",
            "      /\n  ,../...\n /       '\\  /\n< '  )     =<\n \\ \\      /  \\\n  `'\\\"'\"'",
        ],
        "color": [
            "       2\n     1112111\n6  11       1\n 66     7  4 5\n6  1      3 1\n    11111311",
            "      2\n  1112111\n 1       11  6\n5 4  7     66\n 1 3      1  6\n  11311111",
        ],
    },
    {
        "shape": [
            "    \\\n\\ /--\\\n>=  (o>\n/ \\__/\n    /",
            "  /\n /--\\ /\n<o)  =<\n \\__/ \\\n  \\",
        ],
        "color": [
            "    2\n6 1111\n66  745\n6 1111\n    3",
            "  2\n 1111 6\n547  66\n 1111 6\n  3",
        ],
    },
    {
        "shape": [
            "       \\:.\n\\;,   ,;\\\\\\\\,,\n  \\\\\\\\;;:::::::o\n  ///;;::::::::<\n /;` ``/////``",
            "      .:/\n   ,,///;,   ,;/\n o:::::::;;///\n>::::::::;;\\\\\\\\\n  ''\\\\\\\\\\\\\\\\'' ';\\",
        ],
        "color": [
            "       222\n666   1122211\n  6661111111114\n  66611111111115\n 666 113333311",
            "      222\n   1122211   666\n 4111111111666\n51111111111666\n  113333311 666",
        ],
    },
    {
        "shape": [
            "  __\n><_'>\n   '",
            " __\n<'_><\n `",
        ],
        "color": [
            "  11\n61145\n   3",
            " 11\n54116\n 3",
        ],
    },
    {
        "shape": [
            "   ..\\\\\n>='   ('>\n  '''/''",
            "  ,..\n<')   `=<\n ``\\```",
        ],
        "color": [
            "   1121\n661   745\n  111311",
            "  1211\n547   166\n 113111",
        ],
    },
    {
        "shape": [
            "   \\\n  / \\\n>=_('>\n  \\_/\n   /",
            "  /\n / \\\n<')_=<\n \\_/\n  \\",
        ],
        "color": [
            "   2\n  1 1\n661745\n  111\n   3",
            "  2\n 1 1\n547166\n 111\n  3",
        ],
    },
    {
        "shape": [
            "  ,\\\n>=('>\n  '/",
            " /,\n<')=<\n \\`",
        ],
        "color": [
            "  12\n66745\n  13",
            " 21\n54766\n 31",
        ],
    },
    {
        "shape": [
            "  __\n\\/ o\\\n/\\__/",
            " __\n/o \\/\n\\__/\\",
        ],
        "color": [
            "  11\n61 41\n61111",
            " 11\n14 16\n11116",
        ],
    },
]

NEW_FISH_DESIGNS = [
    {
        "shape": [
            "   \\\n  / \\\n>=_('>\n  \\_/\n   /",
            "  /\n / \\\n<')_=<\n \\_/\n  \\",
        ],
        "color": [
            "   1\n  1 1\n663745\n  111\n   3",
            "  2\n 111\n547366\n 111\n  3",
        ],
    },
    {
        "shape": [
            "     ,\n     }\\\\\n\\  .'  `\\\n}}<   ( 6>\n/  `,  .'\n     }/\n     '",
            "    ,\n   /{\n /'  `.  /\n<6 )   >{{\n `.  ,'  \\\n   {\\\n    `",
        ],
        "color": [
            "     2\n     22\n6  11  11\n661   7 45\n6  11  11\n     33\n     3",
            "    2\n   22\n 11  11  6\n54 7   166\n 11  11  6\n   33\n    3",
        ],
    },
    {
        "shape": [
            "            \\'`.\n             )  \\\n(`.      _.-`' ' '`-.\n \\ `.  .`        (o) \\_\n  >  ><     (((       (\n / .`  ._      /_|  /'\n(.`       `-. _  _.-`\n            /__/'",
            "       .'`/\n      /  (\n  .-'` ` `'-._      .')\n_/ (o)        '.  .' /\n)       )))     ><  <\n`\\  |_\\      _.'  '. \\\n  '-._  _ .-'       '.)\n      `\\__\\",
        ],
        "color": [
            "            1111\n             1  1\n111      11111 1 1111\n 1 11  11        141 11\n  1  11     777       5\n 1 11  111      333  11\n111       111 1  1111\n            11111",
            "       1111\n      1  1\n  1111 1 11111      111\n11 141        11  11 1\n5       777     11  1\n11  333      111  11 1\n  1111  1 111       111\n      11111",
        ],
    },
    {
        "shape": [
            "       ,--,_\n__    _\\.---'-.\n\\ '.-\"     // o\\\n/_.'-._    \\\\  /\n       `\"--(/\"`",
            "    _,--,\n .-'---./_    __\n/o \\\\     \"-.' /\n\\  //    _.-'._\\\n `\"\\)--\"`",
        ],
        "color": [
            "       22222\n66    121111211\n6 6111     77 41\n6661111    77  1\n       11113311",
            "    22222\n 112111121    66\n14 77     1116 6\n1  77    1111666\n 11331111",
        ],
    },
]

FISH_DESIGNS = OLD_FISH_DESIGNS + NEW_FISH_DESIGNS


def rand_color(color_mask: str) -> str:
    """Replace numbered placeholders with random colors"""
    colors = ["c", "C", "r", "R", "y", "Y", "b", "B", "g", "G", "m", "M"]
    result = color_mask
    for i in range(1, 10):
        color = random.choice(colors)
        result = result.replace(str(i), color)
    return result


def add_fish(old_fish: Optional[Entity], anim: Any, classic_mode: bool = False):
    """Add a new fish to the aquarium"""
    if classic_mode:
        fish_design = random.choice(OLD_FISH_DESIGNS)
    else:
        if random.randint(1, 12) > 8:
            fish_design = random.choice(NEW_FISH_DESIGNS)
        else:
            fish_design = random.choice(OLD_FISH_DESIGNS)

    direction = random.randint(0, 1)

    shape = fish_design["shape"][direction]
    color_mask = fish_design["color"][direction]

    color_mask = rand_color(color_mask)

    speed = random.uniform(0.25, 2.0)
    if direction == 1:
        speed *= -1

    depth = random.randint(DEPTH["fish_start"], DEPTH["fish_end"])

    fish_entity = Entity(
        entity_type="fish",
        shape=shape,
        auto_trans=True,
        color=color_mask,
        position=[0, 0, depth],
        callback=fish_callback,
        callback_args=[speed, 0, 0],
        die_offscreen=True,
        death_cb=add_fish,
        physical=True,
        coll_handler=fish_collision,
    )

    fish_entity.base_dx = speed

    water_line_bottom = 9
    screen_bottom = anim.height() - 1
    available_height = screen_bottom - water_line_bottom - fish_entity.height

    if available_height > 0:
        fish_entity.y = random.randint(
            water_line_bottom, water_line_bottom + available_height
        )
    else:
        fish_entity.y = water_line_bottom

    if direction == 0:
        fish_entity.x = -fish_entity.width
    else:
        fish_entity.x = anim.width()

    anim.add_entity(fish_entity)


def add_all_fish(anim: Any, classic_mode: bool = False):
    """Add initial population of fish"""
    screen_size = (anim.height() - 9) * anim.width()
    fish_count = max(1, screen_size // 350)

    for _ in range(fish_count):
        add_fish(None, anim, classic_mode)