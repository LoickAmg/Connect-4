"""Tests unitaires de la logique pure (pas de dépendance à pygame)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.board import (  # noqa: E402
    PLAYER_ONE,
    PLAYER_TWO,
    ColumnFullError,
    ConnectFour,
    InvalidColumnError,
)


def test_empty_board_has_no_winner():
    board = ConnectFour()
    assert board.winner == 0
    assert not board.game_over


def test_pieces_stack_with_gravity():
    board = ConnectFour()
    board.drop_piece(3)
    board.drop_piece(3)
    assert board.grid[5][3] == PLAYER_ONE
    assert board.grid[4][3] == PLAYER_TWO


def test_players_alternate():
    board = ConnectFour()
    assert board.current_player == PLAYER_ONE
    board.drop_piece(0)
    assert board.current_player == PLAYER_TWO


def test_horizontal_win():
    board = ConnectFour()
    # P1 joue 0,1,2,3 en bas ; P2 joue ailleurs entre-temps.
    moves = [0, 0, 1, 1, 2, 2, 3]
    for col in moves:
        board.drop_piece(col)
    assert board.game_over
    assert board.winner == PLAYER_ONE


def test_vertical_win():
    board = ConnectFour()
    moves = [0, 1, 0, 1, 0, 1, 0]
    for col in moves:
        board.drop_piece(col)
    assert board.game_over
    assert board.winner == PLAYER_ONE


def test_diagonal_win():
    board = ConnectFour()
    # Construit une diagonale montante pour PLAYER_ONE en colonnes 0-3.
    moves = [0, 1, 1, 2, 2, 3, 2, 3, 3, 0, 3]
    for col in moves:
        board.drop_piece(col)
    assert board.game_over
    assert board.winner == PLAYER_ONE


def test_column_full_raises():
    board = ConnectFour(rows=2, cols=2)
    board.drop_piece(0)
    board.drop_piece(0)
    with pytest.raises(ColumnFullError):
        board.drop_piece(0)


def test_invalid_column_raises():
    board = ConnectFour()
    with pytest.raises(InvalidColumnError):
        board.drop_piece(99)


def test_reset_clears_board():
    board = ConnectFour()
    board.drop_piece(2)
    board.reset()
    assert board.grid[5][2] == 0
    assert board.current_player == PLAYER_ONE
    assert not board.game_over
