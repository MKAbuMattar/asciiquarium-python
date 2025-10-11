import random
from typing import Any, Optional

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

    if cb_args[0] > 0:
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


def fish_callback(fish: Entity, anim: Any) -> bool:
    """Fish behavior - occasionally blow bubbles (matches original probability)"""
    if random.randint(1, 100) > 97:
        add_bubble(fish, anim)
    return fish.move_entity(anim)


def fish_collision(fish: Entity, anim: Any):
    """Handle fish collision with predators and fishing hook"""
    from .special import retract

    for col_obj in fish.collisions():
        if col_obj.entity_type == "teeth" and fish.height <= 5:
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
