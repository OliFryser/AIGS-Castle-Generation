import pygame
from Unit import Unit
from Target import Target


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
