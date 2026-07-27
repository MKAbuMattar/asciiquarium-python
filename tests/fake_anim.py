"""A stand-in for Animation with no curses attached.

Everything the spawners and the entity helpers ask of the animation is either
a screen dimension or a list operation, so the whole draw layer can stay out
of the tests.
"""

from typing import Any, Dict, List

from asciiquarium.entity import Entity


class FakeAnim:
    def __init__(self, entities: Any = (), height: int = 24, width: int = 80):
        self.entities: List[Entity] = list(entities)
        self._height = height
        self._width = width

    def height(self) -> int:
        return self._height

    def width(self) -> int:
        return self._width

    def new_entity(self, **kwargs: Dict[str, Any]) -> Entity:
        entity = Entity(**kwargs)  # type: ignore[arg-type]
        self.add_entity(entity)
        return entity

    def add_entity(self, entity: Entity) -> None:
        self.entities.append(entity)

    def del_entity(self, entity: Entity) -> None:
        if entity in self.entities:
            self.entities.remove(entity)

    def get_entities_of_type(self, entity_type: str) -> List[Entity]:
        return [e for e in self.entities if e.entity_type == entity_type]
