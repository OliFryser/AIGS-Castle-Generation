from TerrainMap import TerrainMap


def saveToFile(terrainMap: TerrainMap, filepath: str):
    with open(filepath, "w") as f:
        # Write terrain
        line = f"{terrainMap.width} {terrainMap.height} {terrainMap.maxHeight}"
        f.write(line + "\n")

        for y in range(terrainMap.height):
            line = " ".join(
                str(terrainMap.getHeight(x, y)) for x in range(terrainMap.width)
            )
            f.write(line + "\n")

        # Write water
        line = f"{len(terrainMap.waterMap)}"
        f.write(line + "\n")

        for x, y in terrainMap.waterMap:
            f.write(f"{x} {y}\n")

        # Write path
        line = f"{len(terrainMap.path)}"
        f.write(line + "\n")

        for x, y in terrainMap.path:
            f.write(f"{x} {y}\n")
