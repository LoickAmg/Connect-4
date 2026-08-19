"""IA simple pour Puissance 4 : minimax avec élagage alpha-bêta.

Aucune dépendance à pygame -> testable directement sur des objets `ConnectFour`.
"""

from __future__ import annotations

import math
import random

from .board import EMPTY, ConnectFour

WINDOW_LENGTH = 4
CENTER_WEIGHT = 3
SCORE_FOUR = 100
SCORE_THREE = 5
SCORE_TWO = 2
SCORE_OPPONENT_THREE = 4


def _other_player(player: int) -> int:
    return 1 if player == 2 else 2


def _score_window(window: list[int], player: int) -> int:
    opponent = _other_player(player)
    player_count = window.count(player)
    empty_count = window.count(EMPTY)
    opponent_count = window.count(opponent)

    if player_count == 4:
        return SCORE_FOUR
    if player_count == 3 and empty_count == 1:
        return SCORE_THREE
    if player_count == 2 and empty_count == 2:
        return SCORE_TWO
    if opponent_count == 3 and empty_count == 1:
        return -SCORE_OPPONENT_THREE
    return 0


def score_position(board: ConnectFour, player: int) -> int:
    """Heuristique de position : plus c'est élevé, meilleur c'est pour `player`."""
    grid = board.grid
    rows, cols = board.rows, board.cols
    score = 0

    center_col = cols // 2
    center_count = sum(1 for row in range(rows) if grid[row][center_col] == player)
    score += center_count * CENTER_WEIGHT

    for row in range(rows):
        for col in range(cols - WINDOW_LENGTH + 1):
            window = [grid[row][col + i] for i in range(WINDOW_LENGTH)]
            score += _score_window(window, player)

    for col in range(cols):
        for row in range(rows - WINDOW_LENGTH + 1):
            window = [grid[row + i][col] for i in range(WINDOW_LENGTH)]
            score += _score_window(window, player)

    for row in range(rows - WINDOW_LENGTH + 1):
        for col in range(cols - WINDOW_LENGTH + 1):
            diag_up = [grid[row + i][col + i] for i in range(WINDOW_LENGTH)]
            score += _score_window(diag_up, player)
            diag_down = [grid[row + WINDOW_LENGTH - 1 - i][col + i] for i in range(WINDOW_LENGTH)]
            score += _score_window(diag_down, player)

    return score


def _ordered_columns(board: ConnectFour) -> list[int]:
    """Essaie les colonnes centrales en premier : améliore l'élagage alpha-bêta."""
    center = board.cols // 2
    return sorted(board.valid_columns(), key=lambda c: abs(c - center))


def _minimax(
    board: ConnectFour,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    ai_player: int,
    opponent: int,
) -> tuple[int | None, float]:
    valid_columns = _ordered_columns(board)
    terminal = board.game_over or not valid_columns

    if depth == 0 or terminal:
        if terminal:
            if board.winner == ai_player:
                return None, math.inf
            if board.winner == opponent:
                return None, -math.inf
            return None, 0  # match nul
        return None, score_position(board, ai_player)

    best_col = random.choice(valid_columns)

    if maximizing:
        value = -math.inf
        for col in valid_columns:
            child = board.clone()
            child.drop_piece(col)
            _, new_score = _minimax(child, depth - 1, alpha, beta, False, ai_player, opponent)
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    value = math.inf
    for col in valid_columns:
        child = board.clone()
        child.drop_piece(col)
        _, new_score = _minimax(child, depth - 1, alpha, beta, True, ai_player, opponent)
        if new_score < value:
            value = new_score
            best_col = col
        beta = min(beta, value)
        if alpha >= beta:
            break
    return best_col, value


def best_move(board: ConnectFour, ai_player: int, depth: int = 4) -> int:
    """Renvoie la colonne choisie par l'IA (minimax + élagage alpha-bêta)."""
    opponent = _other_player(ai_player)
    col, _ = _minimax(board, depth, -math.inf, math.inf, True, ai_player, opponent)
    return col
