import pygame
import sys
import mlxp


@mlxp.launch(config_path="./conf")
def main(ctx: mlxp.Context) -> None:
    # Initialize pygame
    pygame.init()
    print(ctx.config.test)
    # Window size
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fortify Simulation")

    cfg = ctx.config

    # Define a grass-green color (R, G, B)
    backgroundColor = (
        cfg.backgroundColor.r,
        cfg.backgroundColor.g,
        cfg.backgroundColor.b,
    )

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background with green
        screen.fill(backgroundColor)

        pygame.display.flip()

    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
