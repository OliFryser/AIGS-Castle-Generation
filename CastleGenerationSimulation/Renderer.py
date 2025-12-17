import pygame
from CastleElement import MaterialType
from Simulation import Simulation
from Units.Unit import Unit
from Target import Target
import random

class Renderer:
    def __init__(self, simulation: Simulation, screen: pygame.Surface, resolution: int):
        self.simulation = simulation
        self.screen = screen
        self.resolution = resolution
        self.font = pygame.font.Font(None, 48)
        self.materialTypeToColor = {
            MaterialType.SANDSTONE: (153, 145, 137),
            MaterialType.STONE: (91, 91, 91),
            MaterialType.PAVEMENT: (80, 80, 80),
            MaterialType.GRANITE: (160, 160, 160),
            MaterialType.WOOD: (102, 58, 1),
            MaterialType.DOOR: (98, 50, 1),
        }

    def render(self):
        self.screen.fill((255, 0, 255))

        self.displayTerrainMap(self.screen)
        self.renderPath()
        self.renderWaterMap()
        self.renderCastleMap()
        for unit in self.simulation.getUnits():
            self.chaosUnitRender(unit)
        self.renderTarget(self.simulation.target)
        return self.screen

    def renderCastleMap(self):
        cellSize = self.resolution
        level = self.simulation.level
        for y in range(level.height):
            for x in range(level.width):

                node = level.nodeGraph.nodes[(x + 0.5, y + 0.5)]
                if node.materialBlock is not None and node.materialBlock.materialType is not MaterialType.WATER:

                    color = self.materialTypeToColor[node.materialBlock.materialType]

                    rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                    pygame.draw.rect(self.screen, color, rect)
                    
                    """
                    if node.materialBlock.materialType is MaterialType.SANDSTONE:
                        rect0 = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                        pygame.draw.rect(self.screen, (53, 46, 33), rect0, 1)
                    """
                        
                
                """
                """
                #for unit debugging
                if node.unit is not None:
                    color = (255, 0, 0)
                    rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                    pygame.draw.rect(self.screen, color, rect)

    def renderPath(self):
        path = self.simulation.level.path
        scale = self.simulation.level.scale
        pygame.draw.lines(
            self.screen,
            (150, 150, 90),
            False,
            [self.modelToViewSpace(pygame.Vector3(pos[0]*scale+0.5, 20, pos[1]*scale+0.5)) for pos in path],
            scale,
        )

    # this is fast and dirty first lvl renderer
    def displayTerrainMap(self, screen):
        cellSize = self.resolution
        level = self.simulation.level
        for r in range(level.height):
            for c in range(level.width):
                height = level.getCell(c, r)
                color = (34, round((height / level.maxHeight) * 255), 34)
                rect = pygame.Rect(c * cellSize, r * cellSize, cellSize, cellSize)
                pygame.draw.rect(screen, color, rect)

    def chaosUnitRender(self, unit: Unit):
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.modelToViewSpace(unit.position),
            # 5,
            unit.size
            * self.resolution
            * (1 + (unit.position[1] / self.simulation.level.maxHeight)),
        )
        if unit.teamName == "attacker":
            color = (0, 0, 255)
        else:
            color = (255, 0, 0)
            
        pygame.draw.circle(
            self.screen,
            color,
            self.modelToViewSpace(unit.position),
            unit.size
            * self.resolution
            * (1 + (unit.position[1] / self.simulation.level.maxHeight))
            + 1,
            # 7,
        )
        if unit.path and len(unit.path) > 1:
            pygame.draw.lines(
                self.screen,
                (255, 255, 0),
                False,
                [self.modelToViewSpace(pos.position) for pos in unit.path],
            )

    def renderTarget(self, target: Target):
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.modelToViewSpace(target.position),
            3,
        )
        pygame.draw.circle(
            self.screen,
            (252, 188, 27),
            self.modelToViewSpace(target.position),
            2,
        )
    
    def renderWaterMap(self):
        waterMap = self.simulation.level.waterMap
        for x, y in waterMap:
            rect = pygame.Rect(
                x * self.resolution,
                y * self.resolution,
                self.resolution,
                self.resolution,
            )
            r = random.randint(-10,10)
            waterColor = (0,0,200 + r)
            pygame.draw.rect(self.screen, waterColor, rect)


    def modelToViewSpace(self, position: pygame.Vector3) -> pygame.Vector2:
        return pygame.Vector2(
            position[0] * self.resolution, position[2] * self.resolution
        )
