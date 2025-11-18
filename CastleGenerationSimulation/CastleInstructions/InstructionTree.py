from __future__ import annotations
import random

from CastleInstructions.InstructionLine import InstructionLine
from CastleInstructions.InstructionToken import InstructionToken
from CastleInstructions.MutationWeights import MutationWeights


class TreeNode:
    def __init__(self, line: InstructionLine):
        self.line = line
        self.children: list[TreeNode] = []
        self._nextChildIndex = 0

    def addChild(self, childNode: TreeNode):
        self.children.append(childNode)

    def getNextChild(self):
        if self._nextChildIndex < len(self.children):
            child = self.children[self._nextChildIndex]
            self._nextChildIndex += 1
            return child
        return None

    def __str__(self):
        return str(self.line)


class InstructionTree:
    def __init__(self, root: InstructionLine):
        self.root = TreeNode(root)
        self.nodes: list[TreeNode] = [self.root]  # flat list for sampling

    def addChild(self, parent: TreeNode, childLine: InstructionLine):
        childNode = TreeNode(childLine)
        self.nodes.append(childNode)
        parent.addChild(childNode)
        return childNode

    def mutate(
        self,
        mutationWeights: MutationWeights,
        node: TreeNode | None = None,
    ):
        if node is None:
            node = self.sampleRandomNode()

        newElement = random.choices(mutationWeights.options, mutationWeights.weights)[0]
        node.line.mutate(newElement)

        if newElement == InstructionToken.BRANCH:
            newBranch = TreeNode(InstructionLine(""))
            node.addChild(newBranch)
            self.nodes.append(newBranch)

    def mutateAdditive(
        self,
        mutationWeights: MutationWeights,
        node: TreeNode | None = None,
    ):
        if node is None:
            node = self.sampleRandomNode()

        newElement = random.choices(mutationWeights.options, mutationWeights.weights)[0]
        node.line.mutateAdditive(newElement)

        if newElement == InstructionToken.BRANCH:
            newBranch = TreeNode(InstructionLine(""))
            node.addChild(newBranch)
            self.nodes.append(newBranch)

    def sampleRandomNode(self):
        return random.choice(self.nodes)

    def insertSubTree(self, newParent: TreeNode, subTreeRoot: TreeNode):
        newParent.addChild(subTreeRoot)

    def getNextChild(self, parent: TreeNode):
        return parent.getNextChild()

    def to_json(self):
        return str(self)

    def __str__(self):
        def recurse(node: TreeNode, depth: int) -> str:
            result = "\t" * depth + str(node.line) + "\n"
            for child in node.children:
                result += recurse(child, depth + 1)
            return result

        return recurse(self.root, 0)
