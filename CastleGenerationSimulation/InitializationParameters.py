from CastleInstructions.InstructionTree import InstructionTree
from TerrainMap import TerrainMap
from TileMap import TileMap


class InitializationParameters:
    def __init__(
        self,
        terrainMap: TerrainMap,
        tileMap: TileMap,
        castleInstructionTree: InstructionTree,
    ):
        self.terrainMap = terrainMap
        self.castleInstructionTree = castleInstructionTree
        self.tileMap = tileMap
