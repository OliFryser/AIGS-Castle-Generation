import random
from collections import deque

from CastleInstructions.InstructionToken import InstructionToken


class InstructionLine:
    def __init__(self, instructions: str):
        self.instructions = deque(
            [InstructionToken(token) for token in instructions.lstrip().split()]
        )

    def mutate(self, newElement: InstructionToken):
        mutationIndex = random.randrange(len(self.instructions))
        del self.instructions[mutationIndex]
        self.instructions.insert(mutationIndex, newElement)

    def getNextInstruction(self):
        return self.instructions.popleft()

    def isEmpty(self):
        return len(self.instructions) <= 0

    def __str__(self):
        return f"{' '.join(str(instruction) for instruction in self.instructions)}"
