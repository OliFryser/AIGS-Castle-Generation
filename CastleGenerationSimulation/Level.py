import numpy as np
class Level:
    def __init__(self):
        self.height = 60
        self.width = 80
        self.createLevel()

    def createLevel(self):
        self.level = np.zeros((self.height,self.width))

    def getLevel(self):
        return self.level

