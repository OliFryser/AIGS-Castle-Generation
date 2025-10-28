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

    i = 0
    running = True
    simulationStarted = False
    mouseButtonHeld = False

    # Main loop
    while running:
        i += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouseButtonHeld = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouseButtonHeld = False

            elif event.type == pygame.KEYDOWN:
                # process key events
                if event.key == pygame.K_SPACE:
                    simulationStarted = True

        if mouseButtonHeld and not simulationStarted:
            drawWall(simulation, resolution, 2)

        if simulationStarted:
            simulation.step()

        if cfg.render:
            renderer.render()

    print(i)
    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


def drawWall(simulation: Simulation, resolution: int, brushSize: int):
    mouse_x, mouse_y = pygame.mouse.get_pos()

    cell_x = mouse_x // resolution
    cell_y = mouse_y // resolution

    level = simulation.level
    brushSize = brushSize // 2
    # Check bounds before accessing
    for dy in range(-brushSize, brushSize + 1):
        for dx in range(-brushSize, brushSize + 1):
            x = cell_x + dx
            y = cell_y + dy

            if withinLevelBounds(simulation, x, y):
                level.level[y][x] = 100100


def withinLevelBounds(simulation, cell_x, cell_y):
    return (
        0 <= cell_x < simulation.level.width and 0 <= cell_y < simulation.level.height
    )


if __name__ == "__main__":
    main()
