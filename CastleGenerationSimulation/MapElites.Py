from dataclasses import dataclass
import random

from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree
from CastleInstructions.InstructionTreeVariation import substitute


@dataclass
class Behavior:
    blocks: int
    area: int

    def __hash__(self):
        return self.blocks.__hash__() + self.area.__hash__()


@dataclass
class ArchiveEntry:
    fitness: float
    individual: InstructionTree
    behavior: Behavior


class MapElites:
    def __init__(self):
        self.archive: dict[Behavior, ArchiveEntry] = {}

    def generateRandomSolution(self):
        # TODO: Better random solution
        return InstructionTree(InstructionLine(""))

    def sampleRandomSolution(self):
        return random.choice(list(self.archive.values()))

    def randomVariation(self, entry: ArchiveEntry):
        substitute(entry.individual)

    def evaluateBehavior(self, entry: ArchiveEntry):
        pass

    def evaluateFitness(self, entry: ArchiveEntry):
        pass

    def run(self, iterations: int, populationSize: int):
        for i in range(iterations):
            if i < populationSize:
                individual: ArchiveEntry = self.generateRandomSolution()
            else:
                individual: ArchiveEntry = self.sampleRandomSolution()
                self.randomVariation(individual)

            # TODO: Simulate the individual
            self.evaluateBehavior(individual)
            self.evaluateFitness(individual)

            if (
                individual.behavior not in self.archive
                or individual.fitness > self.archive[individual.behavior].fitness
            ):
                self.archive[individual.behavior] = individual
