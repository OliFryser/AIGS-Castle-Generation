import pygame
from TerrainMap import TerrainMap


class TerrainBuilderRenderer:
    def __init__(self, terrainMap: TerrainMap, resolution: int, statusBarOffset: int):
        self.resolution = resolution
        self.statusBarOffset = statusBarOffset
        self.terrainMap = terrainMap
        self.surface = pygame.Surface(
            (terrainMap.width * resolution, terrainMap.height * resolution)
        ).convert()
        self.terrainMapCached = False
        self.waterColor = (40, 50, 255)
        self.pathColor = (120, 60, 30)

    def render(self, screen: pygame.surface.Surface):
        if not self.terrainMapCached:
            self.rerenderTerrainMap(self.terrainMap)
            self.renderWaterMap(self.terrainMap)
            self.renderPath(self.terrainMap)

        screen.blit(self.surface, (0, self.statusBarOffset))

    def renderWaterMap(self, terrainMap: TerrainMap):
        for x, y in terrainMap.waterMap:
            rect = pygame.Rect(
                x * self.resolution,
                y * self.resolution,
                self.resolution,
                self.resolution,
            )
            self.surface.fill(self.waterColor, rect)

    def renderPath(self, terrainMap: TerrainMap):
        for x, y in terrainMap.path:
            rect = pygame.Rect(
                x * self.resolution,
                y * self.resolution,
                self.resolution,
                self.resolution,
            )
            self.surface.fill(self.pathColor, rect)

    def rerenderTerrainMap(self, terrainMap: TerrainMap):
        for y in range(terrainMap.height):
            for x in range(terrainMap.width):
                height = self.terrainMap.getHeight(x, y)
                color = (34, height / self.terrainMap.maxHeight * 255, 34)
                self.drawTerrainTile(x, y, color)

        self.terrainMapCached = True

    def drawTerrainTile(self, x, y, color):
        rect = pygame.Rect(
            x * self.resolution, y * self.resolution, self.resolution, self.resolution
        )
        self.surface.fill(color, rect)

    def modelToViewSpace(self, x, y) -> tuple[int, int]:
        return (
            x * self.resolution,
            y * self.resolution + self.statusBarOffset,
        )
