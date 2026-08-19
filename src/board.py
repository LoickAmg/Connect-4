"""Logique pure du Puissance 4 (sans dépendance à pygame) -> facilement testable."""

from __future__ import annotations

EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = 2

_WIN_DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]


class ColumnFullError(Exception):
    """Levée quand on tente de jouer dans une colonne pleine."""


class InvalidColumnError(Exception):
    """Levée quand la colonne demandée est hors grille."""


class ConnectFour:
    def __init__(self, rows: int = 6, cols: int = 7) -> None:
        self.rows = rows
        self.cols = cols
        self.grid: list[list[int]] = [[EMPTY] * cols for _ in range(rows)]
        self.current_player = PLAYER_ONE
        self.winner = EMPTY
        self.game_over = False
        self.last_move: tuple[int, int] | None = None

    def is_valid_column(self, col: int) -> bool:
        return 0 <= col < self.cols and self.grid[0][col] == EMPTY

    def is_full(self) -> bool:
        return all(self.grid[0][c] != EMPTY for c in range(self.cols))

    def _next_open_row(self, col: int) -> int:
        for row in range(self.rows - 1, -1, -1):
            if self.grid[row][col] == EMPTY:
                return row
        raise ColumnFullError(f"Colonne {col} pleine")

    def drop_piece(self, col: int) -> int:
        """Joue un pion dans la colonne `col` pour le joueur courant.

        Renvoie la ligne où le pion a atterri. Lève `InvalidColumnError` /
        `ColumnFullError` si le coup est illégal, et n'agit plus une fois la
        partie terminée.
        """
        if self.game_over:
            raise RuntimeError("La partie est terminée")
        if not (0 <= col < self.cols):
            raise InvalidColumnError(f"Colonne {col} hors grille")
        if self.grid[0][col] != EMPTY:
            raise ColumnFullError(f"Colonne {col} pleine")

        row = self._next_open_row(col)
        self.grid[row][col] = self.current_player
        self.last_move = (row, col)

        if self._check_win(row, col):
            self.winner = self.current_player
            self.game_over = True
        elif self.is_full():
            self.game_over = True
        else:
            self.current_player = (
                PLAYER_TWO if self.current_player == PLAYER_ONE else PLAYER_ONE
            )

        return row

    def _count_direction(self, row: int, col: int, dr: int, dc: int, player: int) -> int:
        count = 0
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def _check_win(self, row: int, col: int) -> bool:
        player = self.grid[row][col]
        if player == EMPTY:
            return False
        for dr, dc in _WIN_DIRECTIONS:
            total = (
                1
                + self._count_direction(row, col, dr, dc, player)
                + self._count_direction(row, col, -dr, -dc, player)
            )
            if total >= 4:
                return True
        return False

    def reset(self) -> None:
        self.grid = [[EMPTY] * self.cols for _ in range(self.rows)]
        self.current_player = PLAYER_ONE
        self.winner = EMPTY
        self.game_over = False
        self.last_move = None
