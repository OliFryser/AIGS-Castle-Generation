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
    print(ctx.config.test)
    # Window size
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fortify Simulation")

    cfg = ctx.config
    initParams = InitializationParameters(cfg)
    simulation = Simulation(initParams)
    
    renderer = Renderer(simulation, screen)
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        simulation.step()
        if cfg.render:
            renderer.render()
            

    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
