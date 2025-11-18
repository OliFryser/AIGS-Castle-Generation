from CastleElement import ElementType


class TileMap:
    def __init__(self, filepath: str):
        self.tileMap = {}
        for element in ElementType:
            with open(filepath + element.value + ".txt", "r") as f:
                content = f.read().strip()
                tiles = [
                    [line.split() for line in block.splitlines()]
                    for block in content.split("\n\n")
                ]
                self.tileMap[element] = tiles
            f.close()
