from datetime import datetime
import json
import os
import random
import copy

from Utils.Timer import Timer
from .ArchiveEntry import ArchiveEntry
from .Behavior import Behavior, Behaviors
from .DynamicCeiling import DynamicCeiling
from .MapElitesPlotter import MapElitesPlotter, PlotRecord
from .ArchiveVisualizer import renderArchive

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
from Simulation import Simulation, State
from TerrainMap import TerrainMap

# for gc debug
import gc
from collections import Counter


class MapElites:
    def __init__(
        self,
        terrainMap: TerrainMap,
        tileMap,
        archiveSavepath: str,
        resolution: int,
        iterations: int,
        useFitnessWithCost: bool,
    ):
        self.behaviorX = "Cost" #"West-East"
        self.behaviorY = "Area" #"South-North"
        self.iterations = iterations

        self.archive: dict[tuple[int, int], ArchiveEntry] = {}
        self.terrainMap: TerrainMap = terrainMap
        self.tileMap = tileMap

        self.dateString = str(datetime.now().strftime("%Y-%m-%d-%H_%M_%S"))
        self.archiveFolderPath = (
            archiveSavepath
            + self.dateString
            + "__"
            + self.behaviorX
            + "_"
            + self.behaviorY
            + "__"
            + str(self.iterations)
            + "/"
        )

        if not os.path.exists(self.archiveFolderPath):
            os.makedirs(self.archiveFolderPath)

        self.plotter = MapElitesPlotter(self.archiveFolderPath)

        self.initializationMutationWeights = MutationWeights(
            wallWeight=2.75,
            towerWeight=0.5,
            leftWeight=1.0,
            rightWeight=1.0,
            branchWeight=0.5,
            emptyWeight=0.2,
        )
        self.variationMutationWeights = MutationWeights(
            wallWeight=2.0,
            towerWeight=1.0,
            leftWeight=1.0,
            rightWeight=1.0,
            branchWeight=0.5,
            emptyWeight=1.0,
        )

        self.resolution = resolution
        self.dynamicKeys = [DynamicCeiling(maximum=120), DynamicCeiling(maximum=1000)]
        self.dynamicKeys[0].floor = 20
        self.dynamicKeys[0].ceiling = 30
        self.getFitness = (
            self.getFitnessWithCost
            if useFitnessWithCost
            else self.getFitnessWithoutCost
        )

    def generateRandomSolution(self):
        # TODO: Better random solution <3
        individual = InstructionTree(InstructionLine(""))
        r = random.randint(10, 50)
        for i in range(r):
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
        elif rand > 0.3:
            remove(individual)
        else:
            pool = list(self.archive.values())
            pool.remove(entry)
            if not pool:
                return
            other = copy.deepcopy(self.sampleRandomSolution(pool).individual)
            crossover(individual, other)

    def getBehavior(self, state: State) -> Behaviors:
        behaviorX = Behavior(state.cost, self.behaviorX)
        behaviorY = Behavior(state.area, self.behaviorY)
        return Behaviors(behaviorX, behaviorY)

    def getKey(self, behaviors: Behaviors):
        key = []
        for i in range(len(self.dynamicKeys)):
            dynamicCeiling = self.dynamicKeys[i]
            behavior = behaviors.getBehaviors()[i]
            if behavior.value > dynamicCeiling.maximum:
                return False
            if dynamicCeiling.redefineCeiling(behavior.value):
                self.reShiftArchive(i)
                pass
            keyValue = dynamicCeiling.calcValue(behavior.value)
            # this is dangerous
            # if keyValue <= 10:
            key.append(keyValue)
        return tuple(key)

    def reShiftArchive(self, keyIndex):
        newArchive: dict[tuple[int, int], ArchiveEntry] = {}

        for k, v in self.archive.items():
            newKeyList = list(k)
            newKeyList[keyIndex] = self.dynamicKeys[keyIndex].calcValue(
                (v.behavior.getBehaviors()[keyIndex].value)
            )
            newKey: tuple[int, int] = (newKeyList[0], newKeyList[1])
            if newKey not in newArchive or v.fitness > newArchive[newKey].fitness:
                newArchive[newKey] = v

        self.archive = newArchive

    def run(self, populationSize: int):
        outerTimer = Timer(
            f"MapElites for {self.iterations} iterations", forcePrint=True
        )
        outerTimer.start()
        initParams: InitializationParameters = InitializationParameters(
            self.terrainMap, self.tileMap
        )
        simulation = Simulation(initParams)

        for i in range(populationSize):
            if i % 10 == 0:
                print("MapElites population initalization:", i)
                print(f"Archive size: {len(self.archive.keys())}")
            individual: InstructionTree = self.generateRandomSolution()

            self.runSimulation(simulation, individual)

        for i in range(self.iterations):
            if i % 10 == 0:
                print("MapElites iteration:", i)
                print(f"Archive size: {len(self.archive.keys())}")

            entry = self.sampleRandomSolution(list(self.archive.values()))
            individual: InstructionTree = copy.deepcopy(entry.individual)
            self.randomVariation(individual, entry)

            self.runSimulation(simulation, individual)

        simulation.reset()

        outerTimer.stop()
        self.plotter.plotMaxFitnessAndQDScore()
        self.plotter.plotCoverage()
        self.saveArchiveToJSON()
        self.saveArchiveVisualization(simulation)
        simulation = None

    def garbageCheck(self):
        # Garbage check!
        gc.collect()
        types = Counter(type(obj) for obj in gc.get_objects())
        print(types.most_common(5))

        """
            count = sum(1 for o in gc.get_objects() if isinstance(o, Node))
            print(f"Iteration {i+1}: {count} instances of Node")
            """

    def runSimulation(self, simulation: Simulation, individual: InstructionTree):
        simulation.prepare(individual)

        timer = Timer("Run simulation")
        timer.start()
        simulation.runSimulation()
        timer.stop()

        state = simulation.getState()

        behavior: Behaviors = self.getBehavior(state)
        fitness: int = self.getFitness(state)

        simulation.reset()
        key = self.getKey(behavior)
        if key is False:
            return

        if key not in self.archive or fitness > self.archive[key].fitness:
            entry = ArchiveEntry(fitness, behavior, individual)
            self.archive[key] = entry

        self.plotter.addRecord(
            PlotRecord(
                self.getMaxFitness(), self.getAverageFitness(), self.getCoverage()
            )
        )

    def saveArchiveVisualization(self, simulation):
        renderArchive(
            self.archiveFolderPath + "visualization.png",
            10,
            self.archive,
            self.tileMap,
            self.terrainMap,
            self.resolution,
            simulation,
        )

    def saveArchiveToJSON(self):
        filepath = self.archiveFolderPath + "rawDump.json"
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

    def getFitnessWithCost(self, state: State):
        castleCost = state.cost
        castleBudget = 100
        overBudget = 0
        steps = state.stepCount
        kills = state.kills * 20
        area = state.area // 2
        
        if castleCost > castleBudget:
            overBudget = castleCost - castleBudget

        return steps + area + kills - overBudget

    def getFitnessWithoutCost(self, state: State):
        return state.stepCount
