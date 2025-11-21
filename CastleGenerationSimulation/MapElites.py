from dataclasses import asdict, dataclass
from datetime import datetime
import json
import random

from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree
from CastleInstructions.InstructionTreeVariation import substitute, add, crossover
from InitializationParameters import InitializationParameters
from MapElitesPlotter import MapElitesPlotter, PlotRecord
from Simulation import Simulation
from TerrainMap import TerrainMap


@dataclass
class Behavior:
    blocks: int
    area: int

    def to_json(self):
        return asdict(self)


@dataclass
class ArchiveEntry:
    fitness: int
    behavior: Behavior
    individual: InstructionTree

    def __str__(self):
        return f"Fitness: {self.fitness}\nBehavior: Blocks {self.behavior.blocks}, area {self.behavior.area}\n{self.individual}"

    def to_json(self):
        return {
            "fitness": self.fitness,
            "behavior": self.behavior.to_json(),
            "individual": self.individual.to_json(),
        }


class MapElites:
    def __init__(self, terrainMap: TerrainMap, tileMap, archiveSavepath: str):
        self.archive: dict[tuple[int, int], ArchiveEntry] = {}
        self.terrainMap: TerrainMap = terrainMap
        self.tileMap = tileMap

        self.JSONDumpsPath = archiveSavepath + "rawDumps/"
        self.visualizationPath = archiveSavepath + "visualization/"
        self.dateString = str(datetime.now().strftime("%Y-%m-%d-%H_%M_%S"))
        self.plotPath = archiveSavepath + "plots/"
        self.plotter = MapElitesPlotter(
            self.plotPath + "plot_" + self.dateString + ".png"
        )

    def generateRandomSolution(self):
        # TODO: Better random solution
        individual = InstructionTree(InstructionLine(""))
        for i in range(20):
            add(individual)
        return individual

    def sampleRandomSolution(self):
        return random.choice(list(self.archive.values())).individual

    def randomVariation(self, individual: InstructionTree):
        add(individual)

    def getBehavior(self, simulation: Simulation) -> Behavior:
        return Behavior(simulation.getState().blocks, simulation.getState().area)

    def getFitness(self, simulation: Simulation) -> int:
        return simulation.getState().stepCount

    def getKey(self, behavior: Behavior):
        maxArea = self.terrainMap.width * self.terrainMap.height
        areaKey = round((behavior.area / maxArea) * 10)
        maxBlocks = maxArea
        blockKey = round((behavior.blocks / maxBlocks) * 10)
        return (blockKey, areaKey)

    def run(self, iterations: int, populationSize: int):
        for i in range(iterations):
            if i < populationSize:
                individual: InstructionTree = self.generateRandomSolution()
            else:
                individual: InstructionTree = self.sampleRandomSolution()
                self.randomVariation(individual)

            initParams: InitializationParameters = InitializationParameters(
                self.terrainMap, self.tileMap, individual
            )
            simulation = Simulation(initParams)
            simulation.runSimulation()
            behavior: Behavior = self.getBehavior(simulation)
            fitness: int = self.getFitness(simulation)
            key = self.getKey(behavior)

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
