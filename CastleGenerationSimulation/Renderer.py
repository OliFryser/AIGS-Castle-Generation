import pygame
from Level import Level


class Renderer:
    def __init__(self, simulation, screen, resolution: int):
        self.simulation = simulation
        self.screen = screen
        self.resolution = resolution

    def render(self):
        # Fill the background with green
        self.screen.fill((255, 0, 255))

        self.chaosDisplay(self.simulation.level, self.screen)
        for unit in self.simulation.units:
            self.chaosUnitRender(unit)
        # swap buffer
        pygame.display.flip()

    # this is fast and dirty first lvl renderer
    def chaosDisplay(self, level: Level, screen):
        cell_size = self.resolution

        for r in range(level.height):
            for c in range(level.width):
                heightColor = round((level.getCell(c, r) / level.max_height) * 255)
                rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, (34, heightColor, 34), rect)

    def chaosUnitRender(self, unit):
        pygame.draw.circle(
            self.screen, (0, 0, 0), (unit.position[0], unit.position[1]), 7
        )
        pygame.draw.circle(
            self.screen, (0, 0, 255), (unit.position[0], unit.position[1]), 5
        )
