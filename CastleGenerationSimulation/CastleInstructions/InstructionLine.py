import random

from CastleInstructions.InstructionToken import InstructionToken


class InstructionLine:
    def __init__(self, instructions: str):
        self.instructions = list(
            [InstructionToken(token) for token in instructions.lstrip().split()]
        )
        self.nextIndex = 0

    def mutate(self, newElement: InstructionToken):
        mutationIndex = random.randrange(len(self.instructions))
        del self.instructions[mutationIndex]
        self.instructions.insert(mutationIndex, newElement)

    def getNextInstruction(self):
        element = self.instructions[self.nextIndex]
        self.nextIndex += 1
        self.nextIndex %= len(self.instructions)
        return element

    def isEmpty(self):
        return len(self.instructions) <= 0

    def getCost(self):
        costMap = {
            InstructionToken.KEEP: 5,
            InstructionToken.WALL: 1,
            InstructionToken.GATE: 3,
            InstructionToken.TOWER: 5,
        }
        cost = 0
        for instruction in self.instructions:
            if instruction not in costMap:
                continue
            cost += costMap[instruction]

        return cost

    def __str__(self):
        return f"{' '.join(str(instruction) for instruction in self.instructions)}"
