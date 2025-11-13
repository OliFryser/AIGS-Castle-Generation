from enum import Enum


class ElementType(Enum):
    KEEP = "keep"
    WALL = "wall"
    TOWER = "tower"
    GATE = "gate"

class MaterialType(Enum):
    WOOD = "W"
    GRANITE = "G"
    STONE = "R"
    SANDSTONE = "S"
    PAVEMENT = "P"
    EMPTY = "empty"

class CastleElement:
    def __init__(self, elementType: ElementType, materialType: MaterialType = MaterialType.WOOD):
        self.elementType = elementType
        self.material = MaterialBlock(materialType)

class MaterialBlock:
    def __init__(self, materialType: MaterialType) -> None:
        self.materialType = materialType
        self.blocking = True
        self.resetParameters()

    def resetParameters(self):
        if self.materialType == MaterialType.WOOD:
            self.health = 100
            self.damageThreshold = 1
            return
        if self.materialType == MaterialType.GRANITE:
            self.health = 500
            self.damageThreshold = 12
            return
        if self.materialType == MaterialType.STONE:
            self.health = 300
            self.damageThreshold = 9
            return
        if self.materialType == MaterialType.SANDSTONE:
            self.health = 200
            self.damageThreshold = 9
            return
        if self.materialType == MaterialType.PAVEMENT:
            self.health = 0
            self.damageThreshold = 0
            self.blocking = False
            return
    
        self.health = 0
        self.damageThreshold = 0

    #I was tired when I made this
    def destroy(self):
        self.castleElement = None
        self = None