from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree


class InstructionTreeParser:
    def convert4SpacesToTab(self, instructions):
        for i, instruction in enumerate(instructions):
            instructions[i] = instruction.replace(" " * 4, "\t")

    def parseInstructionTree(self, filepath: str):
        with open(filepath, "r") as f:
            instructions = [line.rstrip() for line in f]
            # Make sure we use real tabs
            self.convert4SpacesToTab(instructions)

        root = InstructionLine(0, instructions[0])
        instructions.remove(instructions[0])
        instructionTree = InstructionTree(root)

        parentStack: list[InstructionLine] = []
        lastInstruction = root
        level = 0
        for instruction in instructions:
            currentLevel = instruction.count("\t")
            if currentLevel > level:
                # go a level deeper
                level += 1
                parentStack.append(lastInstruction)
            if currentLevel < level:
                # go a level back
                level -= 1
                parentStack.pop()

            parsedInstruction = InstructionLine(
                instructionTree.getNextId(), instruction
            )
            instructionTree.addChild(parentStack[-1], parsedInstruction)
            lastInstruction = parsedInstruction
        return instructionTree
