from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionTree import InstructionTree, TreeNode


def convert4SpacesToTab(instructions):
    for i, instruction in enumerate(instructions):
        instructions[i] = instruction.replace(" " * 4, "\t")


def convertEscapedTabToTab(instructions: list[str]):
    for i, instruction in enumerate(instructions):
        instructions[i] = instruction.replace("\\t", "\t")


def parseInstructionTree(filepath: str):
    with open(filepath, "r") as f:
        instructions = flatten([line.split("\\n") for line in f])
        convert4SpacesToTab(instructions)
        convertEscapedTabToTab(instructions)

    print(instructions)

    root = InstructionLine(instructions[0])
    instructions.remove(instructions[0])
    instructionTree = InstructionTree(root)

    parentStack: list[TreeNode] = [instructionTree.root]
    lastInstruction = instructionTree.root
    level = 0
    for instruction in instructions:
        currentLevel = instruction.count("\t") + instruction.count("\\t")
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


# Source - https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
# Posted by Alex Martelli, modified by community. See post 'Timeline' for change history
# Retrieved 2025-12-18, License - CC BY-SA 4.0
def flatten(xss):
    return [x for xs in xss for x in xs]
