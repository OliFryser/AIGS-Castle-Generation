from CastleInstructions.InstructionTree import InstructionTree
from CastleInstructions.MutationWeights import MutationWeights


def substitute(instructionTree: InstructionTree):
    mutationWeights = MutationWeights(1.0, 1.0, 1.0, 1.0, 0.1)
    instructionTree.mutate(mutationWeights)


def add(instructionTree: InstructionTree):
    mutationWeights = MutationWeights(1.0, 1.0, 1.0, 1.0, 0.1)
    instructionTree.mutateAdditive(mutationWeights)


def crossover(firstTree: InstructionTree, secondTree: InstructionTree):
    newParent = firstTree.sampleRandomNode()
    subtree = secondTree.sampleRandomNode()
    firstTree.insertSubTree(newParent, subtree)
