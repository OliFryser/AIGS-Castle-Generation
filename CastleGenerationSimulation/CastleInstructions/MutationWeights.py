from CastleInstructions.InstructionToken import InstructionToken


class MutationWeights:
    def __init__(
        self,
        wallWeight: float,
        towerWeight: float,
        leftWeight: float,
        rightWeight: float,
        branchWeight: float,
        emptyWeight: float,
    ):
        self.options = [
            InstructionToken.WALL,
            InstructionToken.TOWER,
            InstructionToken.LEFT,
            InstructionToken.RIGHT,
            InstructionToken.BRANCH,
            InstructionToken.EMPTY,
        ]
        self.weights = [wallWeight, towerWeight, leftWeight, rightWeight, branchWeight, emptyWeight]
