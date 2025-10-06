import random
from typing import Any, Optional

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
    speed = 0.8 if direction == 0 else -0.8

    x = -53 if direction == 0 else anim.width() - 2
    min_y = 9
    max_y = max(9, anim.height() - 11)
    if max_y > min_y:
        y = random.randint(min_y, max_y)
    else:
        y = min_y

    teeth_x = x + (-9 if direction == 0 else 9)
    teeth_y = y + 7

    anim.new_entity(
        entity_type="teeth",
        shape="*",
        position=[teeth_x, teeth_y, 3],
        callback_args=[speed, 0, 0],
        physical=True,
    )

    anim.new_entity(
        entity_type="shark",
        color=shark_colors[direction],
        shape=shark_shapes[direction],
        auto_trans=True,
        position=[x, y, 2],
        default_color="WHITE",
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
    speed = 0.5 if direction == 0 else -0.5
    x = -24 if direction == 0 else anim.width() - 2

    anim.new_entity(
        color=ship_colors[direction],
        shape=ship_shapes[direction],
        auto_trans=True,
        position=[x, 0, 5],
        default_color="WHITE",
        callback_args=[speed, 0, 0],
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
        position=[x, 0, 4],
        default_color="WHITE",
        callback_args=[speed, 0, 0, 1],
        die_offscreen=True,
        death_cb=random_object,
    )


def add_monster(old_ent: Optional[Entity], anim: Any):
    """Add a sea monster"""
    monster_shapes = [
        [
            "\n         _   _                   _   _       _a_a\n       _{.`=`.}_     _   _     _{.`=`.}_    {/ ''\\_\n _    {.'  _  '.}   {.`'`.}   {.'  _  '.}  {|  ._oo)\n{ \\  {/  .' '.  \\}  {/ .-. \\}  {/  .' '.  \\} {/  |",
            "\n                      _   _                    _a_a\n  _      _   _     _{.`=`.}_     _   _      {/ ''\\_\n { \\    {.`'`.}   {.'  _  '.}   {.`'`.}    {|  ._oo)\n  \\ \\  {/ .-. \\}  {/  .' '.  \\}  {/ .-. \\}   {/  |",
        ],
        [
            "\n   a_a_       _   _                   _   _\n _/'' \\}    _{.`=`.}_     _   _     _{.`=`.}_\n(oo_.  |}  {.'  _  '.}   {.`'`.}   {.'  _  '.}    _\n    |  \\} {/  .' '.  \\}  {/ .-. \\}  {/  .' '.  \\}  / }",
            "\n   a_a_                    _   _\n _/'' \\}      _   _     _{.`=`.}_     _   _      _\n(oo_.  |}    {.`'`.}   {.'  _  '.}   {.`'`.}    / }\n    |  \\}   {/ .-. \\}  {/  .' '.  \\}  {/ .-. \\}  / /",
        ],
    ]

    monster_color = "\n   W W\n\n\n\n"

    direction = random.randint(0, 1)
    speed = 0.8 if direction == 0 else -0.8
    x = -54 if direction == 0 else anim.width() - 2

    anim.new_entity(
        shape=monster_shapes[direction],
        auto_trans=True,
        color=[monster_color, monster_color],
        position=[x, 2, 4],
        callback_args=[speed, 0, 0, 0.25],
        death_cb=random_object,
        die_offscreen=True,
        default_color="GREEN",
    )


def add_big_fish(old_ent: Optional[Entity], anim: Any):
    """Add a large fish"""
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
    speed = 1.0 if direction == 0 else -1.0
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
        position=[x, y, 2],
        callback_args=[speed, 0, 0],
        death_cb=random_object,
        die_offscreen=True,
        default_color="YELLOW",
    )


RANDOM_OBJECTS = [
    add_ship,
    add_whale,
    add_monster,
    add_big_fish,
    add_shark,
]


def random_object(dead_object: Optional[Entity], anim: Any):
    """Spawn a random special object"""
    spawner = random.choice(RANDOM_OBJECTS)
    spawner(dead_object, anim)
