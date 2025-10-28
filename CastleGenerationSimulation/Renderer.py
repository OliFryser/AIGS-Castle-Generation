import pygame
from Target import Target
from Level import Level


class Renderer:
    def __init__(self, simulation, screen, resolution: int):
        self.simulation = simulation
        self.screen = screen
        self.resolution = resolution

    def render(self):
        # Fill the background with green
        self.screen.fill((255, 0, 255))

        self.chaosDisplay(self.screen)
        for unit in self.simulation.units:
            self.chaosUnitRender(unit)
        self.renderTarget(self.simulation.target)
        # swap buffer
        pygame.display.flip()

    # this is fast and dirty first lvl renderer
    def chaosDisplay(self, screen):
        cell_size = self.resolution
        level = self.simulation.level
        for r in range(level.height):
            for c in range(level.width):
                height = level.getCell(c, r)
                if height <= level.max_height:
                    color = (34, round((height / level.max_height) * 255), 34)
                else:
                    color = (148, 148, 148)
                rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, color, rect)

    def chaosUnitRender(self, unit):
        pygame.draw.circle(self.screen, (0, 0, 0), (unit.position[0]* self.resolution, unit.position[1]* self.resolution), unit.size * self.resolution * ((1 + (unit.position[2]/self.simulation.level.max_height))))
        pygame.draw.circle(self.screen, (0, 0, 255), (unit.position[0]* self.resolution, unit.position[1]* self.resolution), unit.size * self.resolution * ((1 + (unit.position[2]/self.simulation.level.max_height))) + 1)

    def renderTarget(self, target: Target):
        pygame.draw.circle(
            self.screen, (0, 0, 0), (target.position[0], target.position[1]), 7
        )
        pygame.draw.circle(
            self.screen, (252, 188, 27), (target.position[0], target.position[1]), 5
        )
