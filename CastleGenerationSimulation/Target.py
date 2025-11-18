from Level import Level


class Target:
    def __init__(self, level: Level):
        self.level = level
        self.position = level.targetPosition

    def isOccupied(self):
        if (
            self.level.nodeGraph.getNodeFromPosition(self.position) is not None
            and self.level.nodeGraph.getNodeFromPosition(self.position).unit is not None
        ):
            return True

        return False
