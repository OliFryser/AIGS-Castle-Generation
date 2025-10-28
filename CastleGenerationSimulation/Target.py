from pygame import Vector2, Vector3

from Level import Level


class Target:
    def __init__(self, level: Level, position: Vector2):
        height = level.getBilinearHeight(position[0], position[1])
        self.position = Vector3(position[0], height, position[1])
