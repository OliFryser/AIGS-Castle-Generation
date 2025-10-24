import numpy as np


class Level:
    def __init__(self, levelFilepath: str):
        self.createLevel(levelFilepath)

    def createLevel(self, levelFilepath: str):
        with open(levelFilepath, "r") as f:
            self.width, self.height, self.max_height = [
                int(x) for x in f.readline().rstrip().split()
            ]
            self.level = np.zeros((self.height, self.width))
            for y in range(self.height):
                line = [int(num) for num in f.readline().rstrip().split()]
                for x in range(self.width):
                    self.level[y][x] = line[x]

    def getLevel(self):
        return self.level

    def getCell(self, x, y):
        return self.level[y][x]
