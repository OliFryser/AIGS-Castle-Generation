from dataclasses import asdict, dataclass


@dataclass
class Behavior:
    value: int | float  # add more types as needed
    name: str


@dataclass
class Behaviors:
    def __init__(self, behaviorX, behaivorY):
        self.behaviors: list[Behavior] = [behaviorX, behaivorY]

    def to_json(self):
        return asdict(self)

    def getBehaviors(self):
        return self.behaviors
