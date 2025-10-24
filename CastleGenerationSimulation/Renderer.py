import pygame
from Level import Level


class Renderer:
    def __init__(self, simulation, screen):
        self.simulation = simulation
        self.screen = screen

        pass

    def render(self):
        # Fill the background with green

        # Define a grass-green color (R, G, B)
        backgroundColor = (
            34,
            139,
            34,
        )
        self.screen.fill(backgroundColor)

        self.chaosDisplay(self.simulation.level, self.screen, backgroundColor)
        for unit in self.simulation.units:
            self.chaosUnitRender(unit)
        # swap buffer
        pygame.display.flip()

    # this is fast and dirty first lvl renderer
    def chaosDisplay(self, level: Level, screen, backgroundColor):
        cell_size = 10

        for r in range(level.height):
            for c in range(level.width):
                color = (
                    backgroundColor[0],
                    round((level.getCell(c, r) / level.max_height) * 255),
                    backgroundColor[2],
                )
                rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, color, rect)

    def chaosUnitRender(self, unit):
        pygame.draw.circle(self.screen, (0,0,0), (unit.position[0], unit.position[1]),7)
        pygame.draw.circle(self.screen, (0,0,255), (unit.position[0], unit.position[1]),5)

