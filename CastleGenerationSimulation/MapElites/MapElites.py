from datetime import datetime
import json
import random
import copy

from Utils.Timer import Timer
from .ArchiveEntry import ArchiveEntry
from .Behavior import Behavior
from .DynamicDiscreteKey import DynamicDiscreteKey
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

import gc
from collections import Counter
from Level import Level


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

        self.initializationMutationWeights = MutationWeights(2.75, 0.5, 1.0, 1.0, 1.0)
        self.variationMutationWeights = MutationWeights(4.0, 0.75, 1.0, 1.0, 0.5)

        self.resolution = resolution
        self.dynamicKeys = [DynamicDiscreteKey(), DynamicDiscreteKey()]

    def generateRandomSolution(self):
        # TODO: Better random solution
        individual = InstructionTree(InstructionLine(""))
        r = random.randint(1,30)
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
        blocks = simulation.getState().blocks
        area = simulation.getState().area
        return Behavior(blocks, area)

    def getFitness(self, simulation: Simulation) -> int:
        return simulation.getState().stepCount

    def getKey(self, behavior: Behavior, simulation: Simulation):
        key = []
        for n in range(len(self.dynamicKeys)):
            dKey = self.dynamicKeys[n]
            bValue = behavior.getBehaviours()[n]
            if bValue > dKey.ceiling:
                #dKey.ceiling = bValue
                dKey.increaseCeiling(bValue)
                print(f"increased max in key new max: {dKey.ceiling}")
                self.reShiftArchive(n)
                pass
            keyValue = dKey.calcValue(bValue)
            key.append(keyValue)
        return tuple(key)
        """
        maxBlocks = self.key0.ceiling
        if behavior.blocks > maxBlocks:
            #TODO redifine key
            pass
        blockKey = self.key0.calcValue(behavior.blocks)

        maxArea = self.key1.ceiling
        if behavior.area > maxArea:
            #TODO redifine key aka reshift archive
            pass
        areaKey = self.key1.calcValue(behavior.area)
        
        return (blockKey, areaKey)
        """
    
    def reShiftArchive(self, keyIndex):
        newArchive: dict[tuple[int, int], ArchiveEntry] = {}
        for k,v in self.archive.items():
            newKey = list(k)
            newKey[keyIndex] = self.dynamicKeys[keyIndex].calcValue((v.behavior.getBehaviours()[keyIndex]))
            newKey = tuple(newKey)
            if newKey not in newArchive.keys() or v.fitness > newArchive[newKey].fitness:
                newArchive[newKey] = v

        self.archive = newArchive

    def getKey2(self, behavior: Behavior, simulation: Simulation):
        maxArea = simulation.getMaxArea()
        areaKey = round(10 / (1 + (behavior.area / (maxArea / 1000))))
        maxBlocks = simulation.getMaxBlocks()
        blockKey = round(10 / (1 +(behavior.blocks / (maxBlocks / 100)) * 10))
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

            timer = Timer("Run simulation")
            timer.start()
            simulation.runSimulation()
            timer.stop()

            behavior: Behavior = self.getBehavior(simulation)
            fitness: int = self.getFitness(simulation)
            key = self.getKey(behavior, simulation)

            if key not in self.archive or fitness > self.archive[key].fitness:
                entry = ArchiveEntry(fitness, behavior, individual)
                self.archive[key] = entry
            print(f"achive size: {len(self.archive.keys())}")
            self.plotter.addRecord(
                PlotRecord(
                    self.getMaxFitness(), self.getAverageFitness(), self.getCoverage()
                )
            )
            
            #Garbage Issue!
            simulation = None
            """
            #gc.collect()
            types = Counter(type(obj) for obj in gc.get_objects())
            print(types.most_common(20))

            all_objects = gc.get_objects()
            count = sum(1 for o in all_objects if isinstance(o, Level))
            print(f"Iteration {i+1}: {count} instances of Simulation")
            """


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
