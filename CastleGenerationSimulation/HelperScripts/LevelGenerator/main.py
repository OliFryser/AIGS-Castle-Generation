import mlxp

from RandomLevelGenerator import RandomLevelGenerator
from PerlinLevelGenerator import PerlinLevelGenerator


@mlxp.launch(config_path="LevelGenerationConfig")
def main(ctx: mlxp.Context):
    cfg = ctx.config
    width = cfg.width
    height = cfg.height
    maxHeight = cfg.maxHeight
    outputFile = cfg.outputFile
    if cfg.generator == "random":
        generator = RandomLevelGenerator(maxHeight)
    else:
        generator = PerlinLevelGenerator(cfg.perlinScale, maxHeight)
    with open(outputFile, "w") as f:
        line = f"{width} {height} {maxHeight}"
        f.write(line + "\n")
        for y in range(height):
            line = " ".join(str(generator.getHeight(x, y)) for x in range(width))
            f.write(line + "\n")

    print(
        f"File '{outputFile}' generated with {height} lines and {width} numbers per line."
    )


if __name__ == "__main__":
    main()
