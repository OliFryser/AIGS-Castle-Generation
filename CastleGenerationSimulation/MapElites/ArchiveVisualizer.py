import pygame

from .ArchiveEntry import ArchiveEntry
from InitializationParameters import InitializationParameters
from Renderer import Renderer
from Simulation import Simulation
from TerrainMap import TerrainMap
from TileMap import TileMap
from Utils.Timer import Timer


def renderArchive(
    savefilePath: str,
    behaviorSpaceDimensions: int,
    archive: dict[tuple[int, int], ArchiveEntry],
    tileMap: TileMap,
    terrainMap: TerrainMap,
    resolution: int,
    simulation,
):
    pygame.init()
    entryDimensions = (terrainMap.width * resolution, terrainMap.height * resolution)

    # Axis titles
    leftAxisPadding = round(0.5 * entryDimensions[1])
    bottomAxisPadding = round(0.5 * entryDimensions[0])
    fontSize = round(0.5 * entryDimensions[0])
    fitnessFontSize = round(0.1 * entryDimensions[0])
    font = pygame.font.SysFont(None, fontSize)
    fitnessFont = pygame.font.SysFont(None, fitnessFontSize)

    padding = 4
    timer = Timer("Render archive", forcePrint=True)
    timer.start()
    renderSurface = pygame.Surface(
        (
            entryDimensions[0] * behaviorSpaceDimensions
            + (behaviorSpaceDimensions + 1) * padding
            + leftAxisPadding,
            entryDimensions[1] * behaviorSpaceDimensions
            + (behaviorSpaceDimensions + 1) * padding
            + bottomAxisPadding,
        )
    )

    renderSurface.fill((30, 30, 48))

    # Render dummy archive
    # dummy = list(archive.values())[0]
    # for y in range(10):
    #     for x in range(10):
    #         entrySurface = pygame.Surface((entryDimensions[0], entryDimensions[1]))
    #         initParams = InitializationParameters(terrainMap, tileMap, dummy.individual)
    #         simulation = Simulation(initParams)
    #         renderer = Renderer(simulation, entrySurface, resolution)
    #         entrySurface = renderer.render()
    #         fitness_text = font.render(f"{entry.fitness:.2f}", True, (255, 255, 255))
    #         entrySurface.blit(
    #             fitness_text, (0.05 * entryDimensions[0], 0.05 * entryDimensions[1])
    #         )  # small offset from top-left
    #         renderSurface.blit(
    #             entrySurface,
    #             (
    #                 leftAxisPadding + padding + x * (entryDimensions[0] + padding),
    #                 padding + y * (entryDimensions[1] + padding),
    #             ),
    #         )
    # initParams = InitializationParameters(terrainMap, tileMap)
    # simulation = Simulation(initParams)

    # Render real archive
    for key, entry in archive.items():
        simulation.prepare(entry.individual)
        entrySurface = pygame.Surface((entryDimensions[0], entryDimensions[1]))
        renderer = Renderer(simulation, entrySurface, resolution)
        entrySurface = renderer.render()
        fitnessText = fitnessFont.render(f"{entry.fitness}", True, (255, 255, 255))
        entrySurface.blit(
            fitnessText, (0.05 * entryDimensions[0], 0.05 * entryDimensions[1])
        )  # small offset from top-left
        renderSurface.blit(
            entrySurface,
            (
                leftAxisPadding + padding + key[0] * (entryDimensions[0] + padding),
                padding + key[1] * (entryDimensions[1] + padding),
            ),
        )
        simulation.reset()

    behaviors = list(archive.values())[0].behavior.getBehaviors()

    xLabel = font.render(behaviors[0].name, True, (230, 230, 240))
    xLabelRect = xLabel.get_rect()
    xLabelRect.center = (
        renderSurface.get_width() // 2,
        renderSurface.get_height() - bottomAxisPadding // 2,
    )
    renderSurface.blit(xLabel, xLabelRect)

    yLabel = font.render(behaviors[1].name, True, (230, 230, 240))
    yLabelRotated = pygame.transform.rotate(yLabel, 90)
    yLabelRect = yLabelRotated.get_rect()
    yLabelRect.center = (leftAxisPadding // 2, renderSurface.get_height() // 2)
    renderSurface.blit(yLabelRotated, yLabelRect)

    pygame.image.save(renderSurface, savefilePath)
    timer.stop()
