from enum import Enum
from CastleInstructions.InstructionToken import InstructionToken

class ElementType(Enum):
    KEEP = "keep"
    WALL = "wall"
    TOWER = "tower"
    GATE = "gate"
    EMPTY = "empty"


class MaterialType(Enum):
    WOOD = "W"
    DOOR = "D"
    GRANITE = "G"
    STONE = "R"
    SANDSTONE = "S"
    PAVEMENT = "P"
    EMPTY = "0"
    WATER = "v"


tokenToElementType: dict[InstructionToken, ElementType] = {
    InstructionToken.KEEP: ElementType.KEEP,
    InstructionToken.WALL: ElementType.WALL,
    InstructionToken.GATE: ElementType.GATE,
    InstructionToken.TOWER: ElementType.TOWER,
    InstructionToken.EMPTY: ElementType.EMPTY,
}


class CastleElement:
    def __init__(self, elementType: ElementType, column: int = 0, row: int = 0):
        self.elementType = elementType
        if elementType == ElementType.EMPTY:
            return None
        self.column = column
        self.row = row
        self.materialBlocks: dict[tuple[int, int], MaterialBlock] = {}
        self.linked = []
        self.directions = []

    def setMaterialBlock(self, x, y, materialType):
        if materialType == MaterialType.EMPTY:
            return
        key = (x + self.row, y+self.column)
        materialBlock = MaterialBlock(materialType, self)
        self.materialBlocks[key] = materialBlock
        if materialType is not MaterialType.DOOR:
            return
        self.linked.append(materialBlock)
        materialBlock.linked = self.linked

    def getMaterialBlockLocal(self, x, y):
        key = (x - self.row, y- self.column)
        if key not in self.materialBlocks:
            return None
        return self.materialBlocks[key]

    def getMaterialBlockGlobal(self, x, y):
        key = (x, y )
        if key not in self.materialBlocks:
            return None
        return self.materialBlocks[key]
    
    def destroyMaterialBlock(self, materialBlock):
        toBeDestroyed = []
        for key,v in self.materialBlocks.items():
            if v == materialBlock:
                toBeDestroyed.append(key)    
                
        for k in toBeDestroyed:
            del self.materialBlocks[k]
            
        if materialBlock in self.linked:
            self.linked.remove(materialBlock)


class MaterialBlock:
    def __init__(
        self, materialType: MaterialType, castleElement: CastleElement | None = None):
        self.materialType = materialType
        self.castleElement = castleElement
        self.node = None
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
        if self.materialType == MaterialType.WATER:
            self.health = 0
            self.damageThreshold = 1000
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
        if self.health <= 0:
            return
        if damage <= 0:
            return
        if self.linked:
            self.takeDamage(damage)
            return
        for link in self.linked:
            link.takeDamage(damage / len(self.linked))

    def destroy(self):
        if self.node is not None:
            self.node.materialBlock = None
        self.nodeDeath()

    def nodeDeath(self):
        self.node = None
        self.linked = None
        if self.castleElement:
            self.castleElement.destroyMaterialBlock(self)
            self.castleElement = None

    def getAsData(self):
        return {
            "materialType": self.materialType.value,
            "health" : self.health
            }