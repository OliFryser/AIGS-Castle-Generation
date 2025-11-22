import os
import pygame

from .ArchiveEntry import ArchiveEntry
from InitializationParameters import InitializationParameters
from Renderer import Renderer
from Simulation import Simulation
from TerrainMap import TerrainMap
from TileMap import TileMap
from Utils.Timer import Timer

# Disable visual for pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"


def renderArchive(
    savefilePath: str,
    behaviorSpaceDimensions: int,
    archive: dict[tuple[int, int], ArchiveEntry],
    tileMap: TileMap,
    terrainMap: TerrainMap,
):
    timer = Timer("Render archive")
    timer.start()
    pygame.init()
    renderSurface = pygame.Surface(
        (
            terrainMap.width * behaviorSpaceDimensions,
            terrainMap.height * behaviorSpaceDimensions,
        )
    )
    for key, entry in archive.items():
        entrySurface = pygame.Surface((terrainMap.width, terrainMap.height))
        initParams = InitializationParameters(terrainMap, tileMap, entry.individual)
        simulation = Simulation(initParams)
        renderer = Renderer(simulation, entrySurface, 1)
        entrySurface = renderer.render()
        renderSurface.blit(
            entrySurface, (key[0] * terrainMap.width, key[1] * terrainMap.height)
        )

        pygame.image.save(renderSurface, savefilePath)

    timer.stop()
