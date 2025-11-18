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
    behavior: Behavior
    individual: InstructionTree


class MapElites:
    def __init__(self):
        self.archive: dict[Behavior, ArchiveEntry] = {}

    def generateRandomSolution(self):
        # TODO: Better random solution
        return InstructionTree(InstructionLine(""))

    def sampleRandomSolution(self):
        return random.choice(list(self.archive.values())).individual

    def randomVariation(self, individual: InstructionTree):
        substitute(individual)

    def evaluateBehavior(self, individual: InstructionTree) -> Behavior:
        raise NotImplementedError

    def evaluateFitness(self, individual: InstructionTree) -> float:
        raise NotImplementedError

    def run(self, iterations: int, populationSize: int):
        for i in range(iterations):
            if i < populationSize:
                individual: InstructionTree = self.generateRandomSolution()
            else:
                individual: InstructionTree = self.sampleRandomSolution()
                self.randomVariation(individual)

            # TODO: Simulate the individual
            behavior: Behavior = self.evaluateBehavior(individual)
            fitness: float = self.evaluateFitness(individual)

            if behavior not in self.archive or fitness > self.archive[behavior].fitness:
                entry = ArchiveEntry(fitness, behavior, individual)
                self.archive[behavior] = entry
