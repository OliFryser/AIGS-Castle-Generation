class InitializationParameters:
    def __init__(self, cfg):
        self.levelFilepath: str = cfg.levelFilepath
        self.castleGenerationFilepath = cfg.castleGenerationFilepath
        self.castleTilesFilepath = cfg.catleTilesFilepath
