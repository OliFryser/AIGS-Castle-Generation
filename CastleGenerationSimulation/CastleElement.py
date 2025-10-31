from enum import Enum


class ElementType(Enum):
    KEEP = 0
    WALL = 1
    TOWER = 2
    GATE = 3


class CastleElement:
    def __init__(self, elementType: ElementType):
        self.elementType = elementType
