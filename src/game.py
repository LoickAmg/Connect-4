"""Boucle de jeu et rendu pygame."""

from __future__ import annotations

import sys

import pygame

from .board import EMPTY, PLAYER_ONE, PLAYER_TWO, ColumnFullError, ConnectFour, InvalidColumnError
from .settings import (
    CELL_SIZE,
    COLOR_BG,
    COLOR_BOARD,
    COLOR_EMPTY,
    COLOR_PLAYER_ONE,
    COLOR_PLAYER_TWO,
    COLOR_TEXT,
    COLS,
    FONT_NAME,
    RADIUS,
    ROWS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Puissance 4")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 28)
        self.board = ConnectFour(rows=ROWS, cols=COLS)
        self.hover_col = COLS // 2

    def piece_color(self, player: int) -> tuple[int, int, int]:
        if player == PLAYER_ONE:
            return COLOR_PLAYER_ONE
        if player == PLAYER_TWO:
            return COLOR_PLAYER_TWO
        return COLOR_EMPTY

    def column_from_x(self, x: int) -> int:
        return max(0, min(self.board.cols - 1, x // CELL_SIZE))

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.MOUSEMOTION:
                self.hover_col = self.column_from_x(event.pos[0])

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.board.game_over:
                    continue
                col = self.column_from_x(event.pos[0])
                try:
                    self.board.drop_piece(col)
                except (ColumnFullError, InvalidColumnError):
                    pass  # coup illégal : on ignore le clic

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.board.game_over:
                    self.board.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

    def draw(self) -> None:
        self.screen.fill(COLOR_BG)

        # Prévisualisation du pion en cours de placement.
        if not self.board.game_over and self.board.is_valid_column(self.hover_col):
            cx = self.hover_col * CELL_SIZE + CELL_SIZE // 2
            cy = CELL_SIZE // 2
            color = self.piece_color(self.board.current_player)
            pygame.draw.circle(self.screen, color, (cx, cy), RADIUS)

        board_top = CELL_SIZE
        pygame.draw.rect(
            self.screen, COLOR_BOARD, (0, board_top, SCREEN_WIDTH, SCREEN_HEIGHT - board_top)
        )

        for row in range(self.board.rows):
            for col in range(self.board.cols):
                cx = col * CELL_SIZE + CELL_SIZE // 2
                cy = board_top + row * CELL_SIZE + CELL_SIZE // 2
                value = self.board.grid[row][col]
                color = COLOR_EMPTY if value == EMPTY else self.piece_color(value)
                pygame.draw.circle(self.screen, color, (cx, cy), RADIUS)

        if self.board.game_over:
            if self.board.winner:
                text = f"Joueur {self.board.winner} gagne — R pour rejouer"
            else:
                text = "Match nul — R pour rejouer"
            msg = self.font.render(text, True, COLOR_TEXT)
            rect = msg.get_rect(center=(SCREEN_WIDTH // 2, CELL_SIZE // 2))
            self.screen.blit(msg, rect)

        pygame.display.flip()

    def run(self) -> None:
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(60)
