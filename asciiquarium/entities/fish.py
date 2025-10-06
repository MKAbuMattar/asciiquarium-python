import random
from typing import Any, Optional

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
        shape=["●", "o", "O", "o", "●"],
        position=[bubble_x, bubble_y, bubble_z],
        callback_args=[0, -1, 0, 0.1],
        die_offscreen=True,
        physical=True,
        coll_handler=bubble_collision,
        default_color="BLUE",
    )


def bubble_collision(bubble: Entity, anim: Any):
    """Handle bubble collision with waterline"""
    for col_obj in bubble.collisions():
        if col_obj.entity_type == "waterline":
            bubble.kill()
            break


def fish_callback(fish: Entity, anim: Any) -> bool:
    """Fish behavior - occasionally blow bubbles"""
    if random.randint(1, 100) > 97:
        add_bubble(fish, anim)
    return fish.move_entity(anim)


def fish_collision(fish: Entity, anim: Any):
    """Handle fish collision with predators"""
    for col_obj in fish.collisions():
        if col_obj.entity_type == "teeth" and fish.height <= 5:
            add_splat(anim, *col_obj.position())
            fish.kill()
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


FISH_DESIGNS = [
    {
        "shape": [
            "   \\\n  / \\\n>=_('>\n  \\_/\n   /",
            "  /\n / \\\n<')_=<\n \\_/\n  \\",
        ],
        "color": [
            "   2\n  1 1\n663745\n  111\n   3",
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
            r"            \\'`."
            + "\n"
            + r"             )  \\"
            + "\n"
            + r"(`.      _.-`' ' '`-."
            + "\n"
            + r" \ `.  .`        (o) \_"
            + "\n"
            + r"  >  ><     (((       ("
            + "\n"
            + r" / .`  ._      /_|  /'"
            + "\n"
            + r"(.`       `-. _  _.-`"
            + "\n"
            + r"            /__/'"
            + "\n",
            r"       .'`/"
            + "\n"
            + r"      /  ("
            + "\n"
            + r"  .-`' ` `'-._      .')"
            + "\n"
            + r"_/ (o)        '..  .' /"
            + "\n"
            + r")       )))     ><  <"
            + "\n"
            + r"`\  |_\      _.'  '. \\"
            + "\n"
            + r"  '-._  _ .-'       '.)"
            + "\n"
            + r"      `\__\\"
            + "\n",
        ],
        "color": [
            "            1111\n             1  1\n111      11111 1 1111\n 1 11  11        141 11\n  1  11     777       5\n 1 11  111      333  11\n111       111 1  1111\n            11111\n",
            "       1111\n      1  1\n  1111 1 11111      111\n11 141        11  11 1\n5       777     11  1\n11  333      111  11 1\n  1111  1 111       111\n      11111\n",
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
            r"   ..\," + "\n" + r">='   ('>" + "\n" + r"  '''/''",
            r"  ,/.." + "\n" + r"<')   `=<" + "\n" + r" ``\```",
        ],
        "color": [
            "   1121\n661   745\n  111311",
            "  1211\n547   166\n 113111",
        ],
    },
    {
        "shape": [
            r"  ,\\" + "\n" + r">=('>" + "\n" + r"  '/",
            r" /," + "\n" + r"<')=<" + "\n" + r" \`",
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


def rand_color(color_mask: str) -> str:
    """Replace numbered placeholders with random colors"""
    colors = ["c", "C", "r", "R", "y", "Y", "b", "B", "g", "G", "m", "M"]
    result = color_mask
    for i in range(1, 10):
        color = random.choice(colors)
        result = result.replace(str(i), color)
    return result


def add_fish(old_fish: Optional[Entity], anim: Any):
    """Add a new fish to the aquarium"""
    fish_design = random.choice(FISH_DESIGNS)

    direction = random.randint(0, 1)

    shape = fish_design["shape"][direction]
    color_mask = fish_design["color"][direction]

    color_mask = rand_color(color_mask)

    speed = random.uniform(0.15, 1.2)
    if direction == 1:
        speed *= -1

    depth = random.randint(3, 20)

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

    max_height = 9
    min_height = anim.height() - fish_entity.height
    if min_height <= max_height:
        fish_entity.y = max_height
    else:
        fish_entity.y = random.randint(max_height, min_height - 1)

    if direction == 0:
        fish_entity.x = 1 - fish_entity.width
    else:
        fish_entity.x = anim.width() - 2

    anim.add_entity(fish_entity)


def add_all_fish(anim: Any):
    """Add initial population of fish"""
    screen_size = (anim.height() - 9) * anim.width()
    fish_count = max(1, screen_size // 350)

    for _ in range(fish_count):
        add_fish(None, anim)
