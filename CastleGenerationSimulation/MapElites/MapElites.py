from datetime import datetime
import json
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
        self.plotter = MapElitesPlotter(self.plotPath + "plot_" + self.dateString)

        self.initializationMutationWeights = MutationWeights(
            wallWeight=2.75,
            towerWeight=0.5,
            leftWeight=1.0,
            rightWeight=1.0,
            branchWeight=0.5,
            emptyWeight=0.0,
        )
        self.variationMutationWeights = MutationWeights(
            wallWeight=2.0,
            towerWeight=0.75,
            leftWeight=1.0,
            rightWeight=1.0,
            branchWeight=0.2,
            emptyWeight=0.4,
        )

        self.resolution = resolution
        self.dynamicKeys = [DynamicCeiling(maximum=150), DynamicCeiling(maximum=1000)]

    def generateRandomSolution(self):
        # TODO: Better random solution
        individual = InstructionTree(InstructionLine(""))
        r = random.randint(1, 50)
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

    #this is minor, but creating an object with multiple pieces of information on it each time is suboptimal 
    def getBehavior(self, simulation: Simulation) -> Behaviors:
        behaviorX = Behavior(simulation.getState().cost, "Cost")
        behaviorY = Behavior(simulation.getState().area, "Area")
        return Behaviors(behaviorX, behaviorY)

    def getFitness(self, simulation: Simulation) -> int:
        return simulation.getState().stepCount

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
            if keyValue <= 10:
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

    def run(self, iterations: int, populationSize: int):
        outerTimer = Timer(f"MapElites for {iterations} iterations", forcePrint=True)
        outerTimer.start()
        initParams: InitializationParameters = InitializationParameters(
            self.terrainMap, self.tileMap, None
        )
        simulation = Simulation(initParams)

        for i in range(iterations):
            if i % 10 == 0:
                print("MapElites iteration:", i)
                #print(f"nodeGraph sanity {len(simulation.level.nodeGraph.graph.keys())}")
                print(f"Archive size: {len(self.archive.keys())}")
            if i < populationSize:
                individual: InstructionTree = self.generateRandomSolution()
            else:
                entry = self.sampleRandomSolution(list(self.archive.values()))
                individual: InstructionTree = copy.deepcopy(entry.individual)
                self.randomVariation(individual, entry)

            simulation.prepare(individual)

            timer = Timer("Run simulation")
            timer.start()
            simulation.runSimulation()
            timer.stop()

            behavior: Behaviors = self.getBehavior(simulation)
            fitness: int = self.getFitness(simulation)

            key = self.getKey(behavior)
            if key is False:
                continue

            if key not in self.archive or fitness > self.archive[key].fitness:
                entry = ArchiveEntry(fitness, behavior, individual)
                self.archive[key] = entry
            self.plotter.addRecord(
                PlotRecord(
                    self.getMaxFitness(), self.getAverageFitness(), self.getCoverage()
                )
            )

            simulation.reset()
            # Garbage Issue!
            """
            #simulation = None
            # gc.collect()
            types = Counter(type(obj) for obj in gc.get_objects())
            print(types.most_common(20))

            all_objects = gc.get_objects()
            count = sum(1 for o in all_objects if isinstance(o, Simulation))
            print(f"Iteration {i+1}: {count} instances of Simulation")
            """
        outerTimer.stop()
        self.plotter.plotMaxFitnessAndQDScore()
        self.plotter.plotCoverage()
        # self.saveArchiveToJSON()
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

    """
    def getFitness(self):
        castleCost = self.level.castleCost
        castleBudget = 100
        overBudget = 0
        if castleCost > castleBudget:
            overBudget = (castleCost - castleBudget) * 20
            #overBudget = overBudget*overBudget
            #print(overBudget)
        return self.stepCount - overBudget
    """