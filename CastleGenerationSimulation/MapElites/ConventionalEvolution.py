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
import gc
from collections import Counter
"""
from Utils.Node import Graph, Node
from CastleElement import CastleElement, MaterialBlock
"""

class ConventionalEvolution(MapElites):
    def __init__(self, terrainMap: TerrainMap, tileMap, archiveSavepath: str, resolution: int):
        super().__init__(terrainMap, tileMap, archiveSavepath, resolution)
    
    
    def randomVariationCE(self, individual: InstructionTree, other: InstructionTree, budget = 10):
        rand = random.random()
        if rand > 0.8:
            crossover(individual, other)
            #trueCrossover(individual,other)
        elif rand > 0.6:
            remove(individual)
        elif rand > 0.3:
            add(individual, self.variationMutationWeights)
        else:
            substitute(individual, self.variationMutationWeights)


    
    def runCE(self, generations: int, populationSize: int):
        outerTimer = Timer(f"conventional for {generations} genrations, population {populationSize}", forcePrint=True)
        outerTimer.start()
        initParams: InitializationParameters = InitializationParameters(
            self.terrainMap, self.tileMap,
        )
        simulation = Simulation(initParams)
        selectionSize = populationSize//5
        population = []
        
        for i in range(populationSize):
            if i % 10 == 0:
                print("Evolutionary population initalization:", i)
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
                
                other: InstructionTree = copy.deepcopy(other)
                
                self.randomVariationCE(first,other)
                population.append(first)

            population.sort(key = lambda individual: self.runSimulationCE(simulation, individual),reverse=True)
            selection = population[:selectionSize] + selection[:5]

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
        self.saveArchiveVisualization(simulation)
        

          
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
