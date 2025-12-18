from TerrainMap import TerrainMap
from TileMap import TileMap


class InitializationParameters:
    def __init__(
        self,
        terrainMap: TerrainMap,
        tileMap: TileMap,
    ):
        self.terrainMap = terrainMap
        self.tileMap = tileMap
