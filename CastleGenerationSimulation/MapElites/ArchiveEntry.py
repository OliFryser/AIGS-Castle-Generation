from dataclasses import dataclass

from CastleInstructions.InstructionTree import InstructionTree
from .Behavior import Behaviors


@dataclass
class ArchiveEntry:
    fitness: int
    behavior: Behaviors
    individual: InstructionTree

    def to_json(self):
        return {
            "fitness": self.fitness,
            "behavior": self.behavior.to_json(),
            "individual": self.individual.to_json(),
        }
