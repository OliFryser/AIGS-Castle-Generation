import pygame
import sys
import mlxp

from Level import Level

#this is fast and dirty first lvl renderer
def chaosDisplay(lvl, screen, backgroundColor):
    cell_size = 10

    for r in range(len(lvl)):
        for c in range(len(lvl[0])):
            color = backgroundColor[0], lvl[r,c], backgroundColor[2]
            rect = pygame.Rect(c * cell_size, r * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

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

    lvl = Level().getLevel()
    print()

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

        chaosDisplay(lvl,screen,backgroundColor)
        #swap buffer
        pygame.display.flip()

    # Quit pygame cleanly
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
