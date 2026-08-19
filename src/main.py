"""Point d'entrée du jeu : affiche le menu puis lance la partie."""

import sys

import pygame

from .game import Game
from .menu import Menu
from .settings import SCREEN_HEIGHT, SCREEN_WIDTH


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Puissance 4")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    config = Menu(screen).run()
    if config is None:
        pygame.quit()
        sys.exit(0)

    Game(config).run()


if __name__ == "__main__":
    main()
