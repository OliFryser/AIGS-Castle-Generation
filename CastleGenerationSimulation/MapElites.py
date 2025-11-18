from dataclasses import asdict, dataclass
import random

from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree
from CastleInstructions.InstructionTreeVariation import substitute, add, crossover
from InitializationParameters import InitializationParameters
from Simulation import Simulation


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
    def __init__(self, terrainMap, tileMap):
        self.archive: dict[tuple[int, int], ArchiveEntry] = {}
        self.terrainMap = terrainMap
        self.tileMap = tileMap

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

    def evaluateBehavior(self, simulation: Simulation) -> Behavior:
        return Behavior(simulation.getState().blocks, simulation.getState().area)

    def evaluateFitness(self, simulation: Simulation) -> int:
        return simulation.getState().stepCount

    def getKey(self, behavior: Behavior):
        return (behavior.area // 10, behavior.blocks // 5)

    def run(self, iterations: int, populationSize: int):
        for i in range(iterations):
            if i < populationSize:
                individual: InstructionTree = self.generateRandomSolution()
            else:
                individual: InstructionTree = self.sampleRandomSolution()
                self.randomVariation(individual)

            # TODO: Simulate the individual
            initParams: InitializationParameters = InitializationParameters(
                self.terrainMap, self.tileMap, individual
            )
            simulation = Simulation(initParams)
            simulation.runSimulation()
            behavior: Behavior = self.evaluateBehavior(simulation)
            fitness: int = self.evaluateFitness(simulation)
            key = self.getKey(behavior)

            if key not in self.archive or fitness > self.archive[key].fitness:
                entry = ArchiveEntry(fitness, behavior, individual)
                self.archive[key] = entry
