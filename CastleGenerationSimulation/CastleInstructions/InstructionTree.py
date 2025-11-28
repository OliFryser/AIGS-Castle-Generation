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

    def replaceChild(self, newChild):
        if self.children:
            childIndex = random.randrange(len(self.children))
            replacedChild = self.children[childIndex]
            del self.children[childIndex]
            self.children.insert(childIndex, newChild)
            return replacedChild

        self.line.instructions.append(InstructionToken.BRANCH)
        self.children.append(newChild)
        return None

    def reset(self):
        self._nextChildIndex = 0
        self.line.reset()

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

    def mutateSubstitute(
        self,
        mutationWeights: MutationWeights,
        node: TreeNode | None = None,
    ):
        if node is None:
            node = self.sampleRandomNode()

        newElement = random.choices(mutationWeights.options, mutationWeights.weights)[0]
        removedElement = node.line.mutate(newElement)

        if newElement == InstructionToken.BRANCH:
            newBranch = TreeNode(InstructionLine(""))
            node.addChild(newBranch)
            self.nodes.append(newBranch)

        if removedElement == InstructionToken.BRANCH:
            # TODO: Consider picking the correct branch rather than just the last one
            branchToRemove = node.children.pop()
            self.removeSubTree(branchToRemove)

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

    def mutateDestructive(self, node: TreeNode | None = None):
        if node is None:
            node = self.sampleRandomNode()

        removedElement = node.line.mutateDestructive()
        if removedElement == InstructionToken.BRANCH:
            # TODO: Consider picking the correct branch rather than just the last one
            # Currently a bug where you can pop from an empty children list (Should not be possible, since a branch should always have a child)
            branchToRemove = node.children.pop()
            self.removeSubTree(branchToRemove)

    def sampleRandomNode(self):
        return random.choice(self.nodes)

    def insertSubTree(self, newParent: TreeNode, subTreeRoot: TreeNode):
        replacedChild = newParent.replaceChild(subTreeRoot)
        if replacedChild:
            self.removeSubTree(replacedChild)

        self.addSubTree(subTreeRoot)

    def addSubTree(self, subTree: TreeNode):
        stack = [subTree]

        while stack:
            node = stack.pop()
            self.nodes.append(node)

            stack.extend(reversed(node.children))

    def removeSubTree(self, subTree: TreeNode):
        stack = [subTree]

        while stack:
            node = stack.pop()
            self.nodes.remove(node)

            stack.extend(reversed(node.children))

    def getNextChild(self, parent: TreeNode):
        return parent.getNextChild()

    def to_json(self):
        return str(self)

    # Reset inner counters so we can build the castle again
    def reset(self):
        for node in self.nodes:
            node.reset()

    def __str__(self):
        def recurse(node: TreeNode, depth: int) -> str:
            result = "\t" * depth + str(node.line) + "\n"
            for child in node.children:
                result += recurse(child, depth + 1)
            return result

        return recurse(self.root, 0)
