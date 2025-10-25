import pygame
import sys
import mlxp

from InitializationParameters import InitializationParameters
from Simulation import Simulation
from Renderer import Renderer


@mlxp.launch(config_path="./conf")
def main(ctx: mlxp.Context) -> None:
    # Initialize pygame
    pygame.init()
    # Window size
    pygame.display.set_caption("Fortify Simulation")

    cfg = ctx.config
    initParams = InitializationParameters(cfg)
    simulation = Simulation(initParams)

    resolution: int = cfg.resolution
    viewportWidth = resolution * simulation.level.width
    viewportHeight = resolution * simulation.level.height
    screen = pygame.display.set_mode((viewportWidth, viewportHeight))

    renderer = Renderer(simulation, screen, resolution)
    # Main loop
    running = True
    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if not simulation.step():

            running = False
        if cfg.render:
            renderer.render()
        i+=1
    print(i)
    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
