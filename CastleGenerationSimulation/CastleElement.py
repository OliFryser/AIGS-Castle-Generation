from enum import Enum


class ElementType(Enum):
    KEEP = "keep"
    WALL = "wall"
    TOWER = "tower"
    GATE = "gate"


class CastleElement:
    def __init__(self, elementType: ElementType):
        self.elementType = elementType
