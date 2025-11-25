from datetime import datetime
import json
import random
import copy

from .ArchiveEntry import ArchiveEntry
from .Behavior import Behavior
from .MapElitesPlotter import MapElitesPlotter, PlotRecord
from .MapElitesVisualizer import renderArchive

from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree
from CastleInstructions.InstructionTreeVariation import (
    substitute,
    add,
    crossover,
    remove,
)
from CastleInstructions.MutationWeights import MutationWeights

from InitializationParameters import InitializationParameters
from Simulation import Simulation
from TerrainMap import TerrainMap


class MapElites:
    def __init__(
        self, terrainMap: TerrainMap, tileMap, archiveSavepath: str, resolution: int
    ):
        self.archive: dict[tuple[int, int], ArchiveEntry] = {}
        self.terrainMap: TerrainMap = terrainMap
        self.tileMap = tileMap

        self.JSONDumpsPath = archiveSavepath + "rawDumps/"
        self.visualizationPath = archiveSavepath + "visualizations/"
        self.dateString = str(datetime.now().strftime("%Y-%m-%d-%H_%M_%S"))
        self.plotPath = archiveSavepath + "plots/"
        self.plotter = MapElitesPlotter(
            self.plotPath + "plot_" + self.dateString + ".png"
        )

        self.initializationMutationWeights = MutationWeights(0.75, 0.5, 1.0, 1.0, 1.0)
        self.variationMutationWeights = MutationWeights(1.0, 0.75, 1.0, 1.0, 0.5)

        self.resolution = resolution

    def generateRandomSolution(self):
        # TODO: Better random solution
        individual = InstructionTree(InstructionLine(""))
        for i in range(20):
            add(individual, self.initializationMutationWeights)
        return individual

    def sampleRandomSolution(self, samplePool: list[ArchiveEntry]):
        return random.choice(samplePool)

    def randomVariation(self, individual: InstructionTree, entry: ArchiveEntry):
        rand = random.random()
        if rand > 0.8:
            add(individual, self.variationMutationWeights)
        elif rand > 0.6:
            substitute(individual, self.variationMutationWeights)
        elif rand > 0.4:
            remove(individual)
        else:
            pool = list(self.archive.values())
            print(pool, entry)
            pool.remove(entry)
            if not pool:
                return
            other = copy.deepcopy(self.sampleRandomSolution(pool).individual)
            crossover(individual, other)

    def getBehavior(self, simulation: Simulation) -> Behavior:
        return Behavior(simulation.getState().blocks, simulation.getState().area)

    def getFitness(self, simulation: Simulation) -> int:
        return simulation.getState().stepCount

    def getKey(self, behavior: Behavior, simulation: Simulation):
        maxArea = simulation.getMaxArea()
        areaKey = round((behavior.area / maxArea) * 10)
        maxBlocks = simulation.getMaxBlocks()
        blockKey = round((behavior.blocks / maxBlocks) * 10)
        return (blockKey, areaKey)

    def run(self, iterations: int, populationSize: int):
        for i in range(iterations):
            if i % 10 == 0:
                print("MapElites iteration:", i)
            if i < populationSize:
                individual: InstructionTree = self.generateRandomSolution()
            else:
                entry = self.sampleRandomSolution(list(self.archive.values()))
                individual: InstructionTree = copy.deepcopy(entry.individual)
                self.randomVariation(individual, entry)

            initParams: InitializationParameters = InitializationParameters(
                self.terrainMap, self.tileMap, individual
            )
            simulation = Simulation(initParams)
            simulation.runSimulation()
            behavior: Behavior = self.getBehavior(simulation)
            fitness: int = self.getFitness(simulation)
            key = self.getKey(behavior, simulation)

            if key not in self.archive or fitness > self.archive[key].fitness:
                entry = ArchiveEntry(fitness, behavior, individual)
                self.archive[key] = entry

            self.plotter.addRecord(
                PlotRecord(
                    self.getMaxFitness(), self.getAverageFitness(), self.getCoverage()
                )
            )
        self.plotter.plot()
        self.saveArchiveToJSON()
        self.saveArchiveVisualization()

    def saveArchiveVisualization(self):
        renderArchive(
            self.visualizationPath + "visual_" + self.dateString + ".png",
            10,
            self.archive,
            self.tileMap,
            self.terrainMap,
            self.resolution,
        )

    def saveArchiveToJSON(self):
        filepath = self.JSONDumpsPath + "rawDump_" + self.dateString + ".json"
        jsonSafeArchive = {str(k): v.to_json() for k, v in self.archive.items()}
        with open(filepath, "x") as fp:
            json.dump(jsonSafeArchive, fp, indent=2)

    # utils for plotting

    def getMaxFitness(self):
        return max(self.archive.values(), key=lambda e: e.fitness).fitness

    # Also called QD-score
    def getAverageFitness(self):
        sum = 0
        for entry in self.archive.values():
            sum += entry.fitness

        return sum / len(self.archive.values())

    def getCoverage(self):
        return len(self.archive.keys())
