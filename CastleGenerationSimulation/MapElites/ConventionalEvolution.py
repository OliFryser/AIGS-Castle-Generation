from datetime import datetime
import json
import random
import copy

from .MapElites import MapElites
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
    trueCrossover,
)
from CastleInstructions.MutationWeights import MutationWeights

from InitializationParameters import InitializationParameters
from Simulation import Simulation, State
from TerrainMap import TerrainMap

#for gc debug
"""
"""
import gc
from collections import Counter
from Utils.Node import Graph, Node
from CastleElement import CastleElement, MaterialBlock

class ConventionalEvolution(MapElites):
    def __init__(self, terrainMap: TerrainMap, tileMap, archiveSavepath: str, resolution: int):
        super().__init__(terrainMap, tileMap, archiveSavepath, resolution)
    
    
    def randomVariationCE(self, individual: InstructionTree, other: InstructionTree, budget = 10):
        rand = random.random()
        cost =0
        if rand > 0.8:
            crossover(individual, other)
            #trueCrossover(individual,other)
            cost = 10
        elif rand > 0.6:
            remove(individual)
            cost = 2
        elif rand > 0.3:
            add(individual, self.variationMutationWeights)
            cost = 2
        else:
            substitute(individual, self.variationMutationWeights)
            cost = 2

        #if budget > 0:
        #    self.randomVariationCE(individual,other, budget-cost)

    
    def runCE(self, generations: int, populationSize: int):
        outerTimer = Timer(f"conventional for {generations} genrations, population {populationSize}", forcePrint=True)
        outerTimer.start()
        initParams: InitializationParameters = InitializationParameters(
            self.terrainMap, self.tileMap, None
        )
        simulation = Simulation(initParams)
        selectionSize = populationSize//5
        population = []
        
        for i in range(populationSize):
            if i % 10 == 0:
                print("Evolutionary population initalization:", i)
                #print(f"nodeGraph sanity {len(simulation.level.nodeGraph.graph.keys())}")
                #print(f"Archive size: {len(self.archive.keys())}")
            individual: InstructionTree = self.generateRandomSolution()
            population.append(individual)
        selection = sorted(population, key = lambda individual: self.runSimulationCE(simulation, individual))[:selectionSize]

        for i in range(generations):
            if i % 10 == 0:
                pass
            print("generation:", i+1)

            population = []
            for j in range(populationSize):
                choices = random.choices(selection,k=2)
                first, other = choices[0],choices[1]
                #first: InstructionTree = copy.deepcopy(first)
                other: InstructionTree = copy.deepcopy(other)
                #trueCrossover(first,other)
                self.randomVariationCE(first,other)
                population.append(first)

            #population.sort(key = lambda individual: self.runSimulationCE(simulation, individual))
            fitnessess = []
            for individual in population:
                fitness = self.runSimulationCE(simulation, individual)
                fitnessess.append(fitness)
                
                """
                # Garbage check!
                gc.collect()
                types = Counter(type(obj) for obj in gc.get_objects())
                print(types.most_common(5))
                """


            #fitnessess.sort(reverse=True)
            population = [x for _, x in sorted(
                        zip(fitnessess, population),
                        key=lambda p: p[0],reverse=True)]
            selection = population[:selectionSize] + selection[:5]

                #print(f"nodeGraph sanity {len(simulation.level.nodeGraph.graph.keys())}")
                #print(f"best fitness: {len(self.archive.keys())}")
        population = population + selection
        for x in range(0,10):
            for y in range(0,10):
                i = x*10 +y
                if i < len(population):
                    fitness = self.runSimulationCE(simulation, population[i])
                    entry = ArchiveEntry(fitness, Behaviors(Behavior(x,"Conventional"),Behavior(y,"Evolution")), population[i])
                    self.archive[(y,x)] = entry

        
        simulation.reset()
        
        
        outerTimer.stop()
        #self.plotter.plotMaxFitnessAndQDScore()
        #self.plotter.plotCoverage()
        # self.saveArchiveToJSON()
        self.saveArchiveVisualization()
        

          
    def runSimulationCE(self, simulation:Simulation, individual: InstructionTree):
        
        simulation.prepare(individual)

        timer = Timer("Run simulation")
        timer.start()
        simulation.runSimulation()
        timer.stop()
        state = simulation.getState()

        fitness: int = self.getFitness(state)

        simulation.reset()

        return fitness
