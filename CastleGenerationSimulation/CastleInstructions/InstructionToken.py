from enum import Enum


class InstructionToken(Enum):
    WALL = "W"
    TOWER = "T"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BRANCH = "BRANCH"
    GATE = "G"
    KEEP = "K"

    def __str__(self):
        return self.value
