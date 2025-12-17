from CastleInstructions.InstructionTree import InstructionTree, TreeNode
from CastleInstructions.InstructionLine import InstructionLine, InstructionToken
from CastleInstructions.MutationWeights import MutationWeights
import random

def substitute(instructionTree: InstructionTree, mutationWeights: MutationWeights):
    instructionTree.mutateSubstitute(mutationWeights)


def add(instructionTree: InstructionTree, mutationWeights: MutationWeights):
    instructionTree.mutateAdditive(mutationWeights)


def remove(instructionTree: InstructionTree):
    instructionTree.mutateDestructive()


def crossover(
    firstTree: InstructionTree,
    secondTree: InstructionTree,
):
    newParent = firstTree.sampleRandomNode()
    subtree = secondTree.sampleRandomNode()
    firstTree.insertSubTree(newParent, subtree)

def trueCrossover(firstTree: InstructionTree, secondTree: InstructionTree):
    nodes = []
    node = tcrec(firstTree.root,secondTree.root, nodes)
    firstTree.root = node
    firstTree.nodes = nodes
    
def tcrec(oneNode:TreeNode, otherNode:TreeNode, acc: list[TreeNode]):

    running = True
    line: list[InstructionToken] = []
    children = []
    
    oneLine = oneNode.line.instructions
    otherLine = otherNode.line.instructions

    while running:
        rLine = random.choice([oneLine,otherLine])
        neoOneNode = oneNode.getNextChild()
        neoOtherNode = otherNode.getNextChild()
        if neoOneNode is None or neoOtherNode is None:
            if InstructionToken.BRANCH in rLine:
                rLine = rLine[:rLine.index(InstructionToken.BRANCH)]
            line = line + rLine
            break
        line = line + rLine
        children.append(tcrec(neoOneNode,neoOtherNode, acc))
            
    instructionLine = InstructionLine("")
    instructionLine.instructions = line

    node = TreeNode(instructionLine)
    node.children = children

    acc.append(node)
    return node