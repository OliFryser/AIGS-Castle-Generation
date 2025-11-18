from enum import Enum
from Utils.Node import Node


class ElementType(Enum):
    KEEP = "keep"
    WALL = "wall"
    TOWER = "tower"
    GATE = "gate"


class MaterialType(Enum):
    WOOD = "W"
    DOOR = "D"
    GRANITE = "G"
    STONE = "R"
    SANDSTONE = "S"
    PAVEMENT = "P"
    EMPTY = "0"


class CastleElement:
    def __init__(self, elementType: ElementType, column: int = 0, row: int = 0):
        self.elementType = elementType
        self.column = column
        self.row = row
        self.materialBlocks: dict[tuple[int, int], MaterialBlock] = {}
        self.linked = []
        self.directions = []

    def setMaterialBlock(self, x, y, materialType):
        if materialType == MaterialType.EMPTY:
            return
        key = (x, y)
        materialBlock = MaterialBlock(materialType, self)
        self.materialBlocks[key] = materialBlock
        if materialType is not MaterialType.DOOR:
            return
        self.linked.append(materialBlock)
        materialBlock.linked = self.linked

    def getMaterialBlockLocal(self, x, y):
        key = (x, y)
        if key not in self.materialBlocks:
            return None
        return self.materialBlocks[key]

    def getMaterialBlockGlobal(self, x, y):
        key = (x - self.row, y - self.column)
        if key not in self.materialBlocks:
            return None
        return self.materialBlocks[key]

    def removeMaterialBlock(self, materialBlock):
        for k, v in self.materialBlocks.items():
            if v == materialBlock:
                del self.materialBlocks[k]


class MaterialBlock:
    def __init__(
        self, materialType: MaterialType, castleElement: CastleElement | None = None
    ) -> None:
        self.materialType = materialType
        self.castleElement = castleElement
        self.node: Node | None = None
        self.blocking = True
        self.linked = []
        self.resetParameters()

    def resetParameters(self):
        if self.materialType == MaterialType.WOOD:
            self.health = 100
            self.damageThreshold = 1
            return
        if self.materialType == MaterialType.DOOR:
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

    def takeDamage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.destroy()

    def hit(self, incommingDamage):
        damage = incommingDamage - self.damageThreshold
        if damage <= 0:
            return
        if len(self.linked) == 0:
            self.takeDamage(damage)
            return
        for link in self.linked:
            link.takeDamage(damage / len(self.linked))

    def destroy(self):
        if self.castleElement is not None:
            self.castleElement.removeMaterialBlock(self)
        if self.node is not None:
            self.node.materialBlock = None
        pass
