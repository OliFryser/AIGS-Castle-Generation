from TerrainMap import TerrainMap
from .MapElites import MapElites

from Utils.Timer import Timer
from .ArchiveEntry import ArchiveEntry
from .Behavior import Behavior, Behaviors
from .DynamicCeiling import DynamicCeiling
from .MapElitesPlotter import MapElitesPlotter, PlotRecord
from .ArchiveVisualizer import renderArchive

import random

class ConventionalEvolution(MapElites):
    def __init__(self, terrainMap: TerrainMap, tileMap, archiveSavepath: str, resolution: int):
        super().__init__(terrainMap, tileMap, archiveSavepath, resolution)
    
    
    def randomVariationCE(self, individual: InstructionTree, other: InstructionTree, budget = 8):
        rand = random.random()
        cost = rand * 10

        if rand > 0.8:
            trueCrossover(individual,other)
        elif rand > 0.6:
            remove(individual)
        elif rand > 0.3:
            add(individual, self.variationMutationWeights)
        else:
            substitute(individual, self.variationMutationWeights)

        if budget > 0:
            self.randomVariationCE(individual,other, budget-cost)
