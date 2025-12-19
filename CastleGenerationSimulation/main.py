import os
import pygame
import sys
import mlxp

from CastleInstructions.InstructionTreeParser import parseInstructionTree
from InitializationParameters import InitializationParameters
from MapElites.MapElites import MapElites
from Simulation import Simulation
from Renderer import Renderer
from TerrainBuilder.TerrainBuilder import TerrainBuilder
from TerrainMap import TerrainMap
from TileMap import TileMap
from MapElites.ConventionalEvolution import ConventionalEvolution
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

    pygame.quit()

    sys.exit()


def runTerrainBuilder(cfg, terrainMap):
    TerrainBuilder(cfg, terrainMap).run()


def runMapElites(cfg, terrainMap, tileMap):
    # Disable visual for pygame
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    mapElites = MapElites(
        terrainMap,
        tileMap,
        cfg.archiveSavepath,
        cfg.resolution,
        cfg.iterations,
        cfg.useFitnessWithCost,
    )
    mapElites.run(cfg.population)


def runConventionalEA(cfg, terrainMap, tileMap):
    # Disable visual for pygame
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    mapElites = ConventionalEvolution(
        terrainMap,
        tileMap,
        cfg.archiveSavepath,
        cfg.resolution,
        cfg.iterations,
        cfg.useFitnessWithCost,
    )
    mapElites.runCE(cfg.population)


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

    # Main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # process key events
                if event.key == pygame.K_SPACE:
                    simulationStarted = True

        if simulationStarted:
            i += 1
            simulation.step()

        renderer.render()
        pygame.display.flip()


if __name__ == "__main__":
    main()
