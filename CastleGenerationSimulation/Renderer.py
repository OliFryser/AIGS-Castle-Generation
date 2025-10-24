import pygame
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
        # swap buffer
        pygame.display.flip()

    
    # this is fast and dirty first lvl renderer
    def chaosDisplay(self, level, screen, backgroundColor):
        cell_size = 10

        for r in range(level.height):
            for c in range(level.width):
                color = backgroundColor[0], level.level[r, c], backgroundColor[2]
                rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, color, rect)

