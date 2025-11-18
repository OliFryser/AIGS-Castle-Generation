from TerrainMap import TerrainMap
from TileMap import TileMap
from Utils.Filepath import Filepath


class InitializationParameters:
    def __init__(self, cfg, terrainMap: TerrainMap, tileMap: TileMap):
        self.terrainMap = terrainMap
        self.castleGenerationFilepath = Filepath(cfg.castleGenerationFilepath)
        self.tileMap = tileMap
