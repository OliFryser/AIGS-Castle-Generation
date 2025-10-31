import pygame
from CastleElement import ElementType
from Simulation import Simulation
from Unit import Unit
from Target import Target


class Renderer:
    def __init__(self, simulation: Simulation, screen, resolution: int):
        self.simulation = simulation
        self.screen = screen
        self.resolution = resolution

        self.font = pygame.font.Font(None, 48)
        self.elementTypeToColor = {
            ElementType.KEEP: (163, 145, 117),
            ElementType.WALL: (91, 91, 91),
            ElementType.TOWER: (160, 160, 160),
            ElementType.GATE: (102, 58, 1),
        }

    def render(self, currentTool: str):
        self.screen.fill((255, 0, 255))

        self.displayTerrainMap(self.screen)
        self.renderCastleMap()
        for unit in self.simulation.units:
            self.chaosUnitRender(unit)
        self.renderTarget(self.simulation.target)

        text = self.font.render(f"Tool: {currentTool}", True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.topleft = (10, 10)
        self.screen.blit(text, text_rect)  # Draw text
        # swap buffer
        pygame.display.flip()

    def renderCastleMap(self):
        cellSize = self.resolution
        level = self.simulation.level
        for y in range(level.height):
            for x in range(level.width):
                castleElement = level.castleMap[y][x]
                if castleElement is not None:
                    color = self.elementTypeToColor[castleElement.elementType]
                    rect = pygame.Rect(x * cellSize, y * cellSize, cellSize, cellSize)
                    pygame.draw.rect(self.screen, color, rect)

    # this is fast and dirty first lvl renderer
    def displayTerrainMap(self, screen):
        cellSize = self.resolution
        level = self.simulation.level
        for r in range(level.height):
            for c in range(level.width):
                height = level.getCell(c, r)
                color = (34, round((height / level.max_height) * 255), 34)
                rect = pygame.Rect(c * cellSize, r * cellSize, cellSize, cellSize)
                pygame.draw.rect(screen, color, rect)

    def chaosUnitRender(self, unit: Unit):
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.modelToViewSpace(unit.position),
            5,
            # unit.size
            # * self.resolution
            # * (1 + (unit.position[1] / self.simulation.level.max_height)),
        )
        pygame.draw.circle(
            self.screen,
            (0, 0, 255),
            self.modelToViewSpace(unit.position),
            # unit.size
            # * self.resolution
            # * (1 + (unit.position[1] / self.simulation.level.max_height))
            # +1
            7,
        )
        if len(unit.path) > 1:
            pygame.draw.lines(
                self.screen,
                (255, 255, 0),
                False,
                [self.modelToViewSpace(pos) for pos in unit.path],
            )

    def renderTarget(self, target: Target):
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            self.modelToViewSpace(target.position),
            7,
        )
        pygame.draw.circle(
            self.screen,
            (252, 188, 27),
            self.modelToViewSpace(target.position),
            5,
        )

    def modelToViewSpace(self, position: pygame.Vector3) -> pygame.Vector2:
        return pygame.Vector2(
            position[0] * self.resolution, position[2] * self.resolution
        )
