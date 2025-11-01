from enum import Enum


class ElementType(Enum):
    KEEP = "keep"
    WALL = "wall"
    TOWER = "tower"
    GATE = "gate"

class MaterialType(Enum):
    WOOD = "wood"
    GRANITE = "granite"
    STONE = "stone"
    SANDSTONE = "sandstone"
    EMPTY = "empty"

class CastleElement:
    def __init__(self, elementType: ElementType, materialType: MaterialType = MaterialType.WOOD):
        self.elementType = elementType
        self.material = MaterialBlock(materialType)

class MaterialBlock:
    def __init__(self, materialType: MaterialType) -> None:
        self.materialType = materialType
        self.resetParameters()

    def resetParameters(self):
        if self.materialType == MaterialType.WOOD:
            self.health = 100
            self.damageThreshold = 1