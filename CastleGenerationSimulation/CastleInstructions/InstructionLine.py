from CastleInstructions.InstructionToken import InstructionToken

from collections import deque


class InstructionLine:
    def __init__(self, id: int, instructions: str):
        self.id = id
        self.instructions = deque(
            [InstructionToken(token) for token in instructions.lstrip().split()]
        )

    def getNextInstruction(self):
        return self.instructions.popleft()

    def getId(self):
        return self.id

    def isEmpty(self):
        return len(self.instructions) > 0

    def __hash__(self):
        return self.id.__hash__()

    def __str__(self):
        return f"{self.id} - {' '.join(str(instruction) for instruction in self.instructions)}"
