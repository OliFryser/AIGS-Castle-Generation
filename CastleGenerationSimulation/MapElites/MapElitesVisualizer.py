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
):
    padding = 4
    entryDimensions = (terrainMap.width * resolution, terrainMap.height * resolution)
    timer = Timer("Render archive")
    timer.start()
    pygame.init()
    renderSurface = pygame.Surface(
        (
            entryDimensions[0] * behaviorSpaceDimensions
            + (behaviorSpaceDimensions + 1) * padding,
            entryDimensions[1] * behaviorSpaceDimensions
            + (behaviorSpaceDimensions + 1) * padding,
        )
    )
    renderSurface.fill((30, 30, 48))
    for key, entry in archive.items():
        entrySurface = pygame.Surface((entryDimensions[0], entryDimensions[1]))
        initParams = InitializationParameters(terrainMap, tileMap, entry.individual)
        simulation = Simulation(initParams)
        renderer = Renderer(simulation, entrySurface, resolution)
        entrySurface = renderer.render()
        renderSurface.blit(
            entrySurface,
            (
                padding + key[0] * (entryDimensions[0] + padding),
                padding + key[1] * (entryDimensions[1] + padding),
            ),
        )

        pygame.image.save(renderSurface, savefilePath)

    timer.stop()
