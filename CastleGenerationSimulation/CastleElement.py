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
        self.material = MaterialBlock(materialType, self)

class MaterialBlock:
    def __init__(self, materialType: MaterialType, castleElement: CastleElement) -> None:
        self.materialType = materialType
        self.resetParameters()
        self.castleElement = castleElement

    def resetParameters(self):
        if self.materialType == MaterialType.WOOD:
            self.health = 100
            self.damageThreshold = 1

    #I was tired when I made this
    def destroy(self):
        self.castleElement = None
        self = None