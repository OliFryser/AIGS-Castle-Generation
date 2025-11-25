from CastleInstructions.InstructionTree import InstructionTree
from CastleInstructions.MutationWeights import MutationWeights


def substitute(instructionTree: InstructionTree, mutationWeights: MutationWeights):
    instructionTree.mutate(mutationWeights)


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
