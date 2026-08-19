"""Constantes de configuration du jeu."""

ROWS = 6
COLS = 7

CELL_SIZE = 100
RADIUS = CELL_SIZE // 2 - 8

SCREEN_WIDTH = CELL_SIZE * COLS
SCREEN_HEIGHT = CELL_SIZE * (ROWS + 1)  # +1 pour la ligne de prévisualisation

COLOR_BG = (17, 17, 17)
COLOR_BOARD = (30, 60, 200)
COLOR_EMPTY = (17, 17, 17)
COLOR_PLAYER_ONE = (220, 60, 60)
COLOR_PLAYER_TWO = (230, 200, 40)
COLOR_TEXT = (240, 240, 240)

FONT_NAME = None  # police par défaut de pygame
