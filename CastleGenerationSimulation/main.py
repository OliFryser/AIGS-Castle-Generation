import pygame
import sys
import mlxp

from InitializationParameters import InitializationParameters
from Simulation import Simulation
from Level import Level


# this is fast and dirty first lvl renderer
def chaosDisplay(level: Level, screen, backgroundColor):
    cell_size = 10

    for r in range(level.height):
        for c in range(level.width):
            color = backgroundColor[0], level.level[r, c], backgroundColor[2]
            rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)


@mlxp.launch(config_path="./conf")
def main(ctx: mlxp.Context) -> None:
    # Initialize pygame
    pygame.init()
    print(ctx.config.test)
    # Window size
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fortify Simulation")

    cfg = ctx.config
    initParams = InitializationParameters(cfg)
    simulation = Simulation(initParams)

    # Define a grass-green color (R, G, B)
    backgroundColor = (
        cfg.backgroundColor.r,
        cfg.backgroundColor.g,
        cfg.backgroundColor.b,
    )

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with green
        screen.fill(backgroundColor)

        chaosDisplay(simulation.level, screen, backgroundColor)
        # swap buffer
        pygame.display.flip()

    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
