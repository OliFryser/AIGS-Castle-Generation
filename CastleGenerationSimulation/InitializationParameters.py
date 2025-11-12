from Utils.Filepath import Filepath


class InitializationParameters:
    def __init__(self, cfg):
        self.levelFilepath = Filepath(cfg.levelFilepath)
        self.castleGenerationFilepath = Filepath(cfg.castleGenerationFilepath)
        self.castleTilesFilepath = Filepath(cfg.catleTilesFilepath)
