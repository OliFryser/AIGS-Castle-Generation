from TerrainMap import TerrainMap
from Utils.Filepath import Filepath


class InitializationParameters:
    def __init__(self, cfg, terrainMap: TerrainMap):
        self.terrainMap = terrainMap
        self.castleGenerationFilepath = Filepath(cfg.castleGenerationFilepath)
        self.castleTilesFilepath = Filepath(cfg.catleTilesFilepath)
