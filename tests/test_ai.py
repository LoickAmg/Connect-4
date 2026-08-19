"""Tests de l'IA (minimax + alpha-bêta) — pas de dépendance à pygame."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ai import best_move  # noqa: E402
from src.board import PLAYER_ONE, PLAYER_TWO, ConnectFour  # noqa: E402


def _make_board(grid: list[list[int]], current_player: int) -> ConnectFour:
    board = ConnectFour(rows=len(grid), cols=len(grid[0]))
    board.grid = [row[:] for row in grid]
    board.current_player = current_player
    return board


def test_ai_takes_immediate_winning_move():
    # L'IA (joueur 2) a trois pions alignés en bas (colonnes 0,1,2) : elle doit jouer 3.
    grid = [[0] * 7 for _ in range(6)]
    grid[5][0] = PLAYER_TWO
    grid[5][1] = PLAYER_TWO
    grid[5][2] = PLAYER_TWO
    grid[5][4] = PLAYER_ONE
    grid[5][5] = PLAYER_ONE
    board = _make_board(grid, PLAYER_TWO)

    col = best_move(board, ai_player=PLAYER_TWO, depth=3)

    assert col == 3


def test_ai_blocks_opponent_immediate_win():
    # Le joueur 1 a trois pions alignés en bas (colonnes 0,1,2) : l'IA (2) doit bloquer en 3.
    grid = [[0] * 7 for _ in range(6)]
    grid[5][0] = PLAYER_ONE
    grid[5][1] = PLAYER_ONE
    grid[5][2] = PLAYER_ONE
    board = _make_board(grid, PLAYER_TWO)

    col = best_move(board, ai_player=PLAYER_TWO, depth=3)

    assert col == 3


def test_ai_returns_valid_column_on_empty_board():
    board = ConnectFour()
    col = best_move(board, ai_player=PLAYER_TWO, depth=2)
    assert board.is_valid_column(col)
