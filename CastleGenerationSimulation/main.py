import pygame
import sys
import mlxp

from CastleElement import CastleElement, ElementType
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
    currentTool = ElementType.KEEP

    # Main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouseButtonHeld = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouseButtonHeld = False

            elif event.type == pygame.KEYDOWN:
                # process key events
                if event.key == pygame.K_1:
                    currentTool = ElementType(0)
                if event.key == pygame.K_2:
                    currentTool = ElementType(1)
                if event.key == pygame.K_3:
                    currentTool = ElementType(2)
                if event.key == pygame.K_4:
                    currentTool = ElementType(3)
                if event.key == pygame.K_0:
                    currentTool = None
                if event.key == pygame.K_SPACE:
                    simulationStarted = True

        if mouseButtonHeld and not simulationStarted:
            drawElement(simulation, resolution, currentTool)

        if simulationStarted:
            i += 1
            simulation.step()

        if cfg.render:
            currentToolName: str = (
                currentTool.name if currentTool is not None else "Eraser"
            )
            renderer.render(currentToolName)

    print(i)
    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


def drawElement(
    simulation: Simulation, resolution: int, currentTool: ElementType | None
):
    mouseX, mouseY = pygame.mouse.get_pos()

    cellX = mouseX // resolution
    cellY = mouseY // resolution

    # Snap to 3x3 grid
    castleGridSize = 3
    brushSize = castleGridSize // 2
    cellX = (cellX // castleGridSize) * castleGridSize + brushSize
    cellY = (cellY // castleGridSize) * castleGridSize + brushSize

    level = simulation.level
    # Check bounds before accessing
    for dy in range(-brushSize, brushSize + 1):
        for dx in range(-brushSize, brushSize + 1):
            x = cellX + dx
            y = cellY + dy

            if withinLevelBounds(simulation, x, y):
                level.castleMap[y][x] = (
                    CastleElement(currentTool) if currentTool is not None else None
                )


def withinLevelBounds(simulation, cell_x, cell_y):
    return (
        0 <= cell_x < simulation.level.width and 0 <= cell_y < simulation.level.height
    )


if __name__ == "__main__":
    main()
