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
