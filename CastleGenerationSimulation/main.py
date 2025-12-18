import os
import pygame
import sys
import mlxp

from CastleElement import CastleElement, ElementType
from CastleInstructions.InstructionTreeParser import parseInstructionTree
from InitializationParameters import InitializationParameters
from MapElites.MapElites import MapElites
from Simulation import Simulation
from Renderer import Renderer
from TerrainBuilder.TerrainBuilder import TerrainBuilder
from TerrainMap import TerrainMap
from TileMap import TileMap
import Utils.Timer


@mlxp.launch(config_path="./conf")
def main(ctx: mlxp.Context) -> None:
    Utils.Timer.printTimer = ctx.config.printTimer
    cfg = getattr(ctx.config, ctx.config.mode)
    terrainMap = TerrainMap(cfg.levelFilepath)
    tileMap = TileMap(ctx.config.castleTilesFilepath)

    match ctx.config.mode:
        case "interactive":
            runInteractiveMode(cfg, terrainMap, tileMap)
        case "mapElites":
            runMapElites(cfg, terrainMap, tileMap)
        case "conventionalEA":
            runConventionalEA(cfg, terrainMap, tileMap)
        case "terrainBuilder":
            runTerrainBuilder(cfg, terrainMap)
    print("before quit")
    pygame.quit()
    print("after quit")

    sys.exit()


def runTerrainBuilder(cfg, terrainMap):
    TerrainBuilder(cfg, terrainMap).run()


def runMapElites(cfg, terrainMap, tileMap):
    # Disable visual for pygame
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    mapElites = MapElites(terrainMap, tileMap, cfg.archiveSavepath, cfg.resolution)
    mapElites.run(cfg.iterations, cfg.population)


def runConventionalEA(cfg, terrainMap, tileMap):
    # Disable visual for pygame
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    mapElites = MapElites(terrainMap, tileMap, cfg.archiveSavepath, cfg.resolution)
    mapElites.runCE(cfg.iterations, cfg.population)


def runInteractiveMode(cfg, terrainMap, tileMap):
    castleInstructionTree = parseInstructionTree(cfg.castleGenerationFilepath)
    initParams = InitializationParameters(terrainMap, tileMap)
    simulation = Simulation(initParams)
    simulation.prepare(castleInstructionTree)

    pygame.init()
    pygame.display.set_caption("Fortify Simulation")

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

        currentToolName: str = currentTool.name if currentTool is not None else "Eraser"

        renderer.render()
        pygame.display.flip()

    print(i)
    # Quit pygame cleanly
    pygame.quit()


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
    if level.castleMap is not None:
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
