import numpy as np


class Level:
    def __init__(self, levelFilepath: str):
        self.height = 60
        self.width = 80
        self.createLevel()

    def createLevel(self):
        self.level = np.random.randint(0, 256, (self.height, self.width))

    def getLevel(self):
        return self.level
