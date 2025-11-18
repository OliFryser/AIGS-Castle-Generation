from CastleInstructions.InstructionToken import InstructionToken


class MutationWeights:
    def __init__(
        self,
        wallWeight: float,
        towerWeight: float,
        leftWeight: float,
        rightWeight: float,
        branchWeight: float,
    ):
        self.options = [
            InstructionToken.WALL,
            InstructionToken.TOWER,
            InstructionToken.LEFT,
            InstructionToken.RIGHT,
            InstructionToken.BRANCH,
        ]
        self.weights = [wallWeight, towerWeight, leftWeight, rightWeight, branchWeight]
