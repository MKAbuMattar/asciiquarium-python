import random
from typing import Any, Optional

from ..animation import DEPTH
from ..entity import Entity


def add_shark(old_ent: Optional[Entity], anim: Any):
    """Add a shark that eats small fish"""
    shark_shapes = [
        """                              __
                             ( `\\
  ,                          )   `\\
;' `.                       (     `\\__
 ;   `.             __..---''          `~~~~-._
  `.   `.____...--''                       (b  `--._
    >                     _.-'      .((      ._     )
  .`.-`--...__         .-'     -.___.....-(|/|/|/|/'
 ;.'         `. ...----`.___.',,,_______......---'
 '           '-'""",
        """                     __
                    /' )
                  /'   (                          ,
              __/'     )                       .' `;
      _.-~~~~'          ``---..__             .'   ;
 _.--'  b)                       ``--...____.'   .'
(     _.      )).      `-._                     <
 `\\|\\|\\|\\|)-.....___.-     `-.         __...--'-.'.
   `---......_______,,,`.___.'----... .'         `.;
                                     `-`           `""",
    ]

    shark_colors = [
        "\n\n\n\n\n                                           cR\n \n                                          cWWWWWWWW\n\n\n",
        "\n\n\n\n        Rc\n\n  WWWWWWWWc\n\n\n\n",
    ]

    direction = random.randint(0, 1)
    x = -53
    y = (
        random.randint(9, max(9, anim.height() - (10 + 9))) + 9
        if anim.height() > 19
        else 9
    )
    teeth_x = -9
    teeth_y = y + 7
    speed = 2

    if direction == 1:
        speed *= -1
        x = anim.width() - 2
        teeth_x = x + 9

    anim.new_entity(
        entity_type="teeth",
        shape="*",
        position=[teeth_x, teeth_y, DEPTH["shark"] + 1],
        callback_args=[speed, 0, 0],
        physical=True,
    )

    anim.new_entity(
        entity_type="shark",
        color=shark_colors[direction],
        shape=shark_shapes[direction],
        auto_trans=True,
        position=[x, y, DEPTH["shark"]],
        default_color="CYAN",
        callback_args=[speed, 0, 0],
        die_offscreen=True,
        death_cb=shark_death,
    )


def shark_death(shark: Entity, anim: Any):
    """When shark dies, kill its teeth and spawn new random object"""
    teeth = anim.get_entities_of_type("teeth")
    for obj in teeth:
        anim.del_entity(obj)
    random_object(shark, anim)


def add_ship(old_ent: Optional[Entity], anim: Any):
    """Add a ship sailing on the surface"""
    ship_shapes = [
        """     |    |    |
    )_)  )_)  )_)
   )___))___))___)\\
  )____)____)_____)\\\\
_____|____|____|____\\\\\\__
\\                   /""",
        """         |    |    |
        (_(  (_(  (_(
      /(___((___((___(
    //(_____(____(____(
__///____|____|____|_____
    \\                   /""",
    ]

    ship_colors = [
        "     y    y    y\n\n                  w\n                   ww\nyyyyyyyyyyyyyyyyyyyywwwyy\ny                   y",
        "         y    y    y\n\n      w\n    ww\nyywwwyyyyyyyyyyyyyyyyyyyy\n    y                   y",
    ]

    direction = random.randint(0, 1)
    speed = 1.0 if direction == 0 else -1.0
    x = -24 if direction == 0 else anim.width() - 2

    anim.new_entity(
        color=ship_colors[direction],
        shape=ship_shapes[direction],
        auto_trans=True,
        position=[x, 0, DEPTH["water_gap1"]],
        default_color="WHITE",
        callback_args=[speed, 0, 0, 0],
        die_offscreen=True,
        death_cb=random_object,
    )


def add_whale(old_ent: Optional[Entity], anim: Any):
    """Add a whale with water spout animation"""
    whale_shapes = [
        """        .-----:
      .'       `.
,    /       (o) \\
\\`._/          ,__)""",
        """    :-----.
  .'       `.
 / (o)       \\    ,
(__,          \\_.'/""",
    ]

    whale_colors = [
        """             C C
           CCCCCCC
           C  C  C
        BBBBBBB
      BB       BB
B    B       BWB B
BBBBB          BBBB""",
        """   C C
 CCCCCCC
 C  C  C
    BBBBBBB
  BB       BB
 B BWB       B    B
BBBB          BBBBB""",
    ]

    water_spouts = [
        "\n\n\n   :",
        "\n\n   :\n   :",
        "\n  . .\n  -:-\n   :",
        "\n  . .\n .-:-.\n   :",
        "\n  . .\n'.-:-.`\n'  :  '",
        "\n\n .- -.\n;  :  ;",
        "\n\n\n;     ;",
    ]

    direction = random.randint(0, 1)
    speed = 0.5 if direction == 0 else -0.5
    x = -18 if direction == 0 else anim.width() - 2
    spout_align = 11 if direction == 0 else 1

    whale_anim = []
    whale_anim_mask = []

    for _ in range(5):
        whale_anim.append("\n\n\n" + whale_shapes[direction])
        whale_anim_mask.append(whale_colors[direction])

    for spout_frame in water_spouts:
        spout_lines = spout_frame.split("\n")
        separator = "\n" + " " * spout_align
        aligned_spout_frame = separator.join(spout_lines)

        whale_frame = aligned_spout_frame + "\n" + whale_shapes[direction]

        whale_anim.append(whale_frame)
        whale_anim_mask.append(whale_colors[direction])

    anim.new_entity(
        color=whale_anim_mask,
        shape=whale_anim,
        auto_trans=True,
        position=[x, 0, DEPTH["water_gap2"]],
        default_color="WHITE",
        callback_args=[speed, 0, 0, 1],
        die_offscreen=True,
        death_cb=random_object,
    )


def add_monster(old_ent: Optional[Entity], anim: Any, classic_mode: bool = False):
    """Add a sea monster - choose between new and old designs"""
    if classic_mode:
        add_old_monster(old_ent, anim)
    else:
        if random.randint(0, 1) == 0:
            add_new_monster(old_ent, anim)
        else:
            add_old_monster(old_ent, anim)


def add_new_monster(old_ent: Optional[Entity], anim: Any):
    """Add a new sea monster with improved animation"""
    monster_shapes = [
        [
            "\n         _   _                   _   _       _a_a\n       _{.`=`.}_     _   _     _{.`=`.}_    {/ ''\\_\n _    {.'  _  '.}   {.`'`.}   {.'  _  '.}  {|  ._oo)\n{ \\  {/  .'~'.  \\}  {/ .-. \\}  {/  .'~'.  \\} {/  |",
            "\n                      _   _                    _a_a\n  _      _   _     _{.`=`.}_     _   _      {/ ''\\_\n { \\    {.`'`.}   {.'  _  '.}   {.`'`.}    {|  ._oo)\n  \\ \\  {/ .-. \\}  {/  .'~'.  \\}  {/ .-. \\}   {/  |",
        ],
        [
            "\n   a_a_       _   _                   _   _\n _/'' \\}    _{.`=`.}_     _   _     _{.`=`.}_\n(oo_.  |}  {.'  _  '.}   {.`'`.}   {.'  _  '.}    _\n    |  \\} {/  .'~'.  \\}  {/ .-. \\}  {/  .'~'.  \\}  / }",
            "\n   a_a_                    _   _\n _/'' \\}      _   _     _{.`=`.}_     _   _      _\n(oo_.  |}    {.`'`.}   {.'  _  '.}   {.`'`.}    / }\n    |  \\}   {/ .-. \\}  {/  .'~'.  \\}  {/ .-. \\}  / /",
        ],
    ]

    monster_colors = [
        "\n                                                W W\n\n\n\n",
        "\n   W W\n\n\n\n",
    ]

    direction = random.randint(0, 1)
    speed = 2.0 if direction == 0 else -2.0
    x = -54 if direction == 0 else anim.width() - 2

    monster_anim_mask = [monster_colors[direction], monster_colors[direction]]

    anim.new_entity(
        shape=monster_shapes[direction],
        auto_trans=True,
        color=monster_anim_mask,
        position=[x, 2, DEPTH["water_gap2"]],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color="GREEN",
    )


def add_old_monster(old_ent: Optional[Entity], anim: Any):
    """Add an old/classic sea monster with 4-frame animation"""
    monster_shapes = [
        [
            "\n                                                          ____\n            __                                          /   o  \\\n          /    \\        _                     _       /     ____ >\n  _      |  __  |     /   \\        _        /   \\   |     |\n | \\     |  ||  |    |     |     /   \\    |     |  |     |",
            "\n                                                          ____\n                                             __         /   o  \\\n             _                     _       /    \\     /     ____ >\n   _       /   \\        _        /   \\   |  __  |   |     |\n  | \\     |     |     /   \\    |     |  |  ||  |   |     |",
            "\n                                                          ____\n                                  __                  /   o  \\\n _                      _       /    \\        _     /     ____ >\n| \\          _        /   \\   |  __  |     /   \\  |     |\n \\ \\       /   \\    |     |  |  ||  |    |     | |     |",
            "\n                                                          ____\n                       __                             /   o  \\\n  _          _       /    \\        _                /     ____ >\n | \\       /   \\   |  __  |     /   \\        _    |     |\n  \\ \\     |     |  |  ||  |    |     |     /   \\  |     |",
        ],
        [
            "\n    ____\n  /  o   \\                                          __\n< ____     \\       _                     _        /    \\\n      |     |   /   \\        _        /   \\     |  __  |      _\n      |     |  |     |     /   \\    |     |    |  ||  |     / |",
            "\n    ____\n  /  o   \\         __\n< ____     \\     /    \\       _                     _\n      |     |   |  __  |    /   \\        _        /   \\       _\n      |     |   |  ||  |   |     |     /   \\     |     |     / |",
            "\n    ____\n  /  o   \\                  __\n< ____     \\     _        /    \\       _                      _\n      |     |  /   \\     |  __  |   /   \\        _          / |\n      |     | |     |    |  ||  |  |     |    /   \\       / /",
            "\n    ____\n  /  o   \\                             __\n< ____     \\                _        /    \\       _          _\n      |     |    _        /   \\     |  __  |   /   \\       / |\n      |     |  /   \\    |     |    |  ||  |  |     |     / /",
        ],
    ]

    monster_colors = [
        "\n\n                                                            W\n\n\n",
        "\n\n     W\n\n\n",
    ]

    direction = random.randint(0, 1)
    speed = 2.0 if direction == 0 else -2.0
    x = -64 if direction == 0 else anim.width() - 2

    monster_anim_mask = [
        monster_colors[direction],
        monster_colors[direction],
        monster_colors[direction],
        monster_colors[direction],
    ]

    anim.new_entity(
        shape=monster_shapes[direction],
        auto_trans=True,
        color=monster_anim_mask,
        position=[x, 2, DEPTH["water_gap2"]],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color="GREEN",
    )


def add_big_fish(old_ent: Optional[Entity], anim: Any):
    """Add a large fish - randomly choose between two designs"""
    if random.randint(0, 2) > 0:
        add_big_fish_2(old_ent, anim)
    else:
        add_big_fish_1(old_ent, anim)


def add_big_fish_1(old_ent: Optional[Entity], anim: Any):
    """Add a large fish (design 1)"""
    big_fish_shapes = [
        """ ______
`"".  `````-----.....__
     `.  .      .       `-.
       :     .     .       `.
 ,     :   .    .          _ :
: `.   :                  (@) `._
 `. `..'     .     =`-.       .__)
   ;     .        =  ~  :     .-"
 .' .'`.   .    .  =.-'  `._ .'
: .'   :               .   .'
 '   .'  .    .     .   .-'
   .'____....----''.'=.'
   ""             .'.'
               ''"'`""",
        """                           ______
          __.....-----'''''  .-""'
       .-'       .      .  .'
     .'       .     .     :
    : _          .    .   :     ,
 _.' (@)                  :   .' :
(__.       .-'=     .     `..' .'
 "-.     :  ~  =        .     ;
   `. _.'  `-.=  .    .   .'`. `.
     `.   .               :   `. :
       `-.   .     .    .  `.   `
          `.=`.``----....____`.
            `.`.             ""
              '`"``""",
    ]

    big_fish_colors = [
        """ 111111
11111  11111111111111111
     11  2      2       111
       1     2     2       11
 1     1   2    2          1 1
1 11   1                  1W1 111
 11 1111     2     1111       1111
   1     2        1  1  1     111
 11 1111   2    2  1111  111 11
1 11   1               2   11
 1   11  2    2     2   111
   111111111111111111111
   11             1111
               11111""",
        """                           111111
          11111111111111111  11111
       111       2      2  11
     11       2     2     1
    1 1          2    2   1     1
 111 1W1                  1   11 1
1111       1111     2     1111 11
 111     1  1  1        2     1
   11 111  1111  2    2   1111 11
     11   2               1   11 1
       111   2     2    2  11   1
          111111111111111111111
            1111             11
              11111""",
    ]

    direction = random.randint(0, 1)
    speed = 3.0 if direction == 0 else -3.0
    x = -34 if direction == 0 else anim.width() - 1

    max_height = 9
    min_height = anim.height() - 15
    if min_height <= max_height:
        y = max_height
    else:
        y = random.randint(max_height, min_height)

    color_mask = big_fish_colors[direction]
    colors = ["c", "C", "r", "R", "y", "Y", "b", "B", "g", "G", "m", "M"]
    for i in range(1, 10):
        color = random.choice(colors)
        color_mask = color_mask.replace(str(i), color)

    anim.new_entity(
        shape=big_fish_shapes[direction],
        auto_trans=True,
        color=color_mask,
        position=[x, y, DEPTH["shark"]],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=True,
        default_color="YELLOW",
    )


def add_big_fish_2(old_ent: Optional[Entity], anim: Any):
    """Add a large fish (design 2)"""
    big_fish_shapes = [
        """                _ _ _
             .='\\ \\ \\`"=,
           .'\\ \\ \\ \\ \\ \\ \\
\\'=._     / \\ \\ \\_\\_\\_\\_\\_\\
\\'=._'.  /\\ \\,-"`- _ - _ - '-.
  \\`=._\\|'.\\/- _ - _ - _ - _- \\
  ;"= ._\\=./_ -_ -_ {`"=_    @ \\
   ;="_-_=- _ -  _ - {"=_"-     \\
   ;_=_--_.,          {_.='   .-/
  ;.="` / ';\\        _.     _.-`
  /_.='/ \\/ /;._ _ _{.-;`/"`
/._=_.'   '/ / / / /{.= /
/.='       `'./_/_.=`{_/""",
        """            _ _ _
        ,="`/ / /'=.
       / / / / / / /'.
      /_/_/_/_/_/ / / \\     _.='/
   .-' - _ - _ -`"-,/ /\\  .'_.='/
  / -_ - _ - _ - _ -\\/.'|/_.=`/
 / @    _="`} _- _- _\\.=/_. =";
/     -"_="}  - _  - _ -=_-_"=;
\\-.   '=._}          ,._--_=_;
 `-._     ._        /;' \\ `"=.;
     `"\\`;-.}_ _ _.;\\ \\/ \\'=._\\
        \\ =.}\\ \\ \\ \\ \\'   '._=_.\\
         \\_}`=._\\_\\.'`       '=.\\""",
    ]

    big_fish_colors = [
        """                1 1 1
             1111 1 11111
           111 1 1 1 1 1 1
11111     1 1 1 11111111111
1111111  11 111112 2 2 2 2 111
  111111111112 2 2 2 2 2 2 22 1
  111 1111 12 22 22 11111    W 1
   11111112 2 2  2 2 111111     1
   111111111          11111   111
  11111 11111        11     1111
  111111 11 1111 1 111111111
1111111   11 1 1 1 1111 1
1111       1111111111111""",
        """            1 1 1
        11111 1 1111
       1 1 1 1 1 1 111
      11111111111 1 1 1     11111
   111 2 2 2 2 211111 11  1111111
  1 22 2 2 2 2 2 2 211111111111
 1 W    11111 22 22 2111111 111
1     111111 2 2  2 2 21111111
111   11111          111111111
 1111     11        111 1 11111
     111111111 1 1111 11 111111
        1 1111 1 1 1 11   1111111
         1111111111111       1111""",
    ]

    direction = random.randint(0, 1)
    speed = 2.5 if direction == 0 else -2.5
    x = -33 if direction == 0 else anim.width() - 1

    max_height = 9
    min_height = anim.height() - 14
    if min_height <= max_height:
        y = max_height
    else:
        y = random.randint(max_height, min_height)

    color_mask = big_fish_colors[direction]
    colors = ["c", "C", "r", "R", "y", "Y", "b", "B", "g", "G", "m", "M"]
    for i in range(1, 10):
        color = random.choice(colors)
        color_mask = color_mask.replace(str(i), color)

    anim.new_entity(
        shape=big_fish_shapes[direction],
        auto_trans=True,
        color=color_mask,
        position=[x, y, DEPTH["shark"]],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=True,
        default_color="YELLOW",
    )


def add_fishhook(old_ent: Optional[Entity], anim: Any):
    """Add a fishing hook that catches fish"""
    hook_image = r"""       o
      ||
      ||
/ \   ||
  \__//
  `--'"""

    point_image = ".\n \n\\\n "

    line_image = "|\n" * 50 + " \n" * 6

    x = 10 + random.randint(0, max(0, anim.width() - 30))
    y_start = -20
    y_line = y_start - 50
    point_x = x + 1
    point_y = y_start + 2

    anim.new_entity(
        entity_type="fishline",
        shape=line_image,
        position=[x + 7, y_line, DEPTH["water_line1"]],
        auto_trans=True,
        callback=fishhook_cb,
        callback_args={"mode": "lowering"},
    )

    anim.new_entity(
        entity_type="fishhook",
        shape=hook_image,
        position=[x, y_start, DEPTH["water_line1"]],
        auto_trans=True,
        die_offscreen=True,
        death_cb=lambda hook, anim: group_death(hook, anim, ["hook_point", "fishline"]),
        default_color="GREEN",
        callback=fishhook_cb,
        callback_args={"mode": "lowering"},
    )

    anim.new_entity(
        entity_type="hook_point",
        shape=point_image,
        position=[point_x, point_y, DEPTH["shark"] + 1],
        physical=True,
        default_color="GREEN",
        callback=fishhook_cb,
        callback_args={"mode": "lowering"},
    )


def fishhook_cb(entity: Entity, anim: Any) -> bool:
    """Move the fishhook - lower it or reel it in if hooked"""
    x, y, z = entity.position()
    mode = None
    if isinstance(entity.callback_args, dict):
        mode = entity.callback_args.get("mode")
    elif entity.callback_args == "hooked":
        mode = "hooked"

    if mode == "hooked":
        y -= 2
        if y < -10:
            y = -10
    else:
        max_depth = int(anim.height() * 0.75)
        if y < max_depth:
            y += 2
        else:
            y = max_depth

    entity.x = x
    entity.y = y
    entity.z = z

    return True


def retract(entity: Entity, anim: Any):
    """Pull the fish, hook, and line back to surface"""
    entity.physical = False

    if entity.entity_type == "fish":
        x, y, z = entity.position()
        z = DEPTH["water_gap2"]
        entity.set_position(x, y, z)
        entity.callback = fishhook_cb
        entity.callback_args = "hooked"
    else:
        entity.callback_args = "hooked"


def group_death(entity: Entity, anim: Any, bound_types: list):
    """Kill all entities of specified types when one dies"""
    for entity_type in bound_types:
        bound_entities = anim.get_entities_of_type(entity_type)
        for obj in bound_entities:
            anim.del_entity(obj)
    random_object(entity, anim)


def add_ducks(old_ent: Optional[Entity], anim: Any):
    """Add three animated ducks swimming on the surface"""
    duck_shapes = [
        [
            """      _          _          _  
,____(')=  ,____(')=  ,____(')<
 \\~~= ')    \\~~= ')    \\~~= ')""",
            """      _          _          _  
,____(')=  ,____(')<  ,____(')=
 \\~~= ')    \\~~= ')    \\~~= ')""",
            """      _          _          _  
,____(')<  ,____(')=  ,____(')=
 \\~~= ')    \\~~= ')    \\~~= ')""",
        ],
        [
            """  _          _          _
>(')____,  =(')____,  =(')____,
 (` =~~/    (` =~~/    (` =~~/""",
            """  _          _          _
=(')____,  >(')____,  =(')____,
 (` =~~/    (` =~~/    (` =~~/""",
            """  _          _          _
=(')____,  =(')____,  >(')____,
 (` =~~/    (` =~~/    (` =~~/""",
        ],
    ]

    duck_colors = [
        """      g          g          g
wwwwwgcgy  wwwwwgcgy  wwwwwgcgy
 wwww Ww    wwww Ww    wwww Ww""",
        """  g          g          g
ygcgwwwww  ygcgwwwww  ygcgwwwww
 wW wwww    wW wwww    wW wwww""",
    ]

    direction = random.randint(0, 1)
    speed = 1.0 if direction == 0 else -1.0
    x = -30 if direction == 0 else anim.width() - 2

    anim.new_entity(
        shape=duck_shapes[direction],
        auto_trans=True,
        color=duck_colors[direction],
        position=[x, 5, DEPTH["water_gap3"]],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color="WHITE",
    )


def add_dolphins(old_ent: Optional[Entity], anim: Any):
    """Add three dolphins jumping in formation"""
    dolphin_shapes = [
        [
            r"""        ,
      __)\
(\_.-'    a`-.
(/~~````(/~^^`""",
            r"""        ,
(\__  __)\
(/~.''    a`-.
    ````\)~^^`""",
        ],
        [
            r"""     ,
   _/(__
.-'a    `-._/)
'^^~\)''''~~\)""",
            r"""     ,
   _/(__  __/)
.-'a    ``.~\)
'^^~(/''''""",
        ],
    ]

    dolphin_colors = [
        "\n\n\n          W",
        "\n\n\n   W",
    ]

    direction = random.randint(0, 1)
    speed = 2.0 if direction == 0 else -2.0
    x = -13 if direction == 0 else anim.width() - 2
    distance = 15 if direction == 0 else -15

    dolphin3 = anim.new_entity(
        shape=dolphin_shapes[direction],
        auto_trans=True,
        color=dolphin_colors[direction],
        position=[x - (distance * 2), 5, DEPTH["water_gap3"]],
        callback_args=[speed, 0, 0, 0.5],
        death_cb=random_object,
        die_offscreen=True,
        default_color="blue",
    )

    dolphin2 = anim.new_entity(
        shape=dolphin_shapes[direction],
        auto_trans=True,
        color=dolphin_colors[direction],
        position=[x - distance, 5, DEPTH["water_gap3"]],
        callback_args=[speed, 0, 0, 0.5],
        death_cb=None,
        die_offscreen=True,
        default_color="BLUE",
    )

    dolphin1 = anim.new_entity(
        shape=dolphin_shapes[direction],
        auto_trans=True,
        color=dolphin_colors[direction],
        position=[x, 5, DEPTH["water_gap3"]],
        callback_args=[speed, 0, 0, 0.5],
        death_cb=None,
        die_offscreen=True,
        default_color="CYAN",
    )


def add_swan(old_ent: Optional[Entity], anim: Any):
    """Add an elegant swan swimming on the surface"""
    swan_shapes = [
        r"""       ___
,_    / _,\
| \   \( \|
|  \_  \\
(_   \_) \
(\_   `   \
 \   -=~  /""",
        r""" ___
/,_ \    _,
|/ )/   / |
  //  _/  |
 / ( /   _)
/   `   _/)
\  ~=-   /""",
    ]

    swan_colors = [
        "\n\n         g\n         yy\n\n\n\n",
        "\n\n g\nyy\n\n\n\n",
    ]

    direction = random.randint(0, 1)
    speed = 1.0 if direction == 0 else -1.0
    x = -10 if direction == 0 else anim.width() - 2

    anim.new_entity(
        shape=swan_shapes[direction],
        auto_trans=True,
        color=swan_colors[direction],
        position=[x, 1, DEPTH["water_gap3"]],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color="WHITE",
    )


RANDOM_OBJECTS = [
    add_ship,
    add_whale,
    add_monster,
    add_big_fish,
    add_shark,
    add_fishhook,
    add_swan,
    add_ducks,
    add_dolphins,
]


def random_object(dead_object: Optional[Entity], anim: Any):
    """Spawn a random special object"""
    spawner = random.choice(RANDOM_OBJECTS)
    spawner(dead_object, anim)
