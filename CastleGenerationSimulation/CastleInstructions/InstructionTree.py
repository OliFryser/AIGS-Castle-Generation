from collections import defaultdict, deque

from CastleInstructions.InstructionLine import InstructionLine


class InstructionTree:
    def __init__(self, root: InstructionLine):
        self.nextId = 0
        self.root: InstructionLine = root
        self.tree: defaultdict[InstructionLine, deque[InstructionLine]] = defaultdict(
            deque
        )

    def addChild(self, parent: InstructionLine, child: InstructionLine):
        self.tree[parent].append(child)

    def getNextId(self):
        self.nextId += 1
        return self.nextId

    def getNextChild(self, parent: InstructionLine):
        return self.tree[parent].popleft()

    def __str__(self):
        result = ""
        childStack = deque()
        childStack.append(self.root)
        while len(childStack) > 0:
            current = childStack.popleft()
            result += str(current) + "\n"
            for child in self.tree[current]:
                childStack.append(child)
        return result


def convert4SpacesToTab(instructions):
    for i, instruction in enumerate(instructions):
        instructions[i] = instruction.replace(" " * 4, "\t")


def parseInstructionTree(filepath: str):
    with open(filepath, "r") as f:
        instructions = [line.rstrip() for line in f]
        # Make sure we use real tabs
        convert4SpacesToTab(instructions)

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

        parsedInstruction = InstructionLine(instructionTree.getNextId(), instruction)
        instructionTree.addChild(parentStack[-1], parsedInstruction)
        lastInstruction = parsedInstruction
    print(f"Parsed tree:\n{instructionTree}")
    return instructionTree
