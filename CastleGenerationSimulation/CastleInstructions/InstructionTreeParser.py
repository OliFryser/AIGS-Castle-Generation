from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree, TreeNode


def convert4SpacesToTab(instructions):
    for i, instruction in enumerate(instructions):
        instructions[i] = instruction.replace(" " * 4, "\t")


def parseInstructionTree(filepath: str):
    with open(filepath, "r") as f:
        instructions = [line.rstrip() for line in f]
        convert4SpacesToTab(instructions)

    root = InstructionLine(instructions[0])
    instructions.remove(instructions[0])
    instructionTree = InstructionTree(root)

    parentStack: list[TreeNode] = [instructionTree.root]
    lastInstruction = instructionTree.root
    level = 0
    for instruction in instructions:
        currentLevel = instruction.count("\t")
        if currentLevel > level:
            # go a level deeper
            parentStack.append(lastInstruction)
        if currentLevel < level:
            # go a level back
            while len(parentStack) - 1 > currentLevel:
                parentStack.pop()

        level = currentLevel
        parsedInstruction = InstructionLine(instruction)
        newChild = instructionTree.addChild(parentStack[-1], parsedInstruction)
        lastInstruction = newChild
    return instructionTree
