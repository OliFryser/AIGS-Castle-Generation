import os


class Filepath:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.setPrefix()

    def getFilepath(self):
        return self.filepath

    def setPrefix(self):
        currentWorkingDirectory = os.getcwd()
        if not currentWorkingDirectory.endswith("CastleGenerationSimulation"):
            self.filepath = "CastleGenerationSimulation/" + self.filepath
