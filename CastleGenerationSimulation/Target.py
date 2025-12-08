from Level import Level
from Team import Team
from Units.Unit import Unit

class Target:
    def __init__(self, level: Level):
        self.level = level
        self.position = level.targetPosition
        self.team: list[Unit] = []
        self.enemies: list[Unit] = []

    def isOccupied(self):
        for unit in self.enemies:
            if unit.position.distance_to(self.position) < 5:
                return True
        if (
            self.level.nodeGraph.getNodeFromPosition(self.position) is not None
            and self.level.nodeGraph.getNodeFromPosition(self.position).unit is not None
            and self.level.nodeGraph.getNodeFromPosition(self.position).unit not in self.team
        ):
            return True

        return False
