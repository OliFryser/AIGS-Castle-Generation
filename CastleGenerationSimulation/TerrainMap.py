import numpy as np


class TerrainMap:
    def __init__(self, levelFilepath: str):
        with open(levelFilepath, "r") as f:
            self.width, self.height, self.maxHeight = [
                int(x) for x in f.readline().rstrip().split()
            ]
            self.map = np.zeros((self.height, self.width))
            for y in range(self.height):
                line = [float(num) for num in f.readline().rstrip().split()]
                for x in range(self.width):
                    self.map[y][x] = line[x]
