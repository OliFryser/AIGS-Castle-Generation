import noise


class PerlinLevelGenerator:
    def __init__(self, scale, maxHeight):
        self.scale = scale
        self.maxHeight = maxHeight

    def getHeight(self, x, y):
        value = noise.pnoise2(
            x / self.scale,
            y / self.scale,
            octaves=6,
            persistence=0.5,
            lacunarity=2.0,
            repeatx=1024,
            repeaty=1024,
            base=42,
        )

        normalized = (value + 1) / 2
        return normalized * self.maxHeight
