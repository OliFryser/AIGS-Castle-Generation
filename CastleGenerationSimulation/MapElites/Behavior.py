from dataclasses import asdict, dataclass


@dataclass
class Behavior:
    blocks: int
    area: int

    def to_json(self):
        return asdict(self)
    
    def getBehaviours(self):
        return [self.blocks, self.area]
