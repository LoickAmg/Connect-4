"""Boucle de jeu et rendu pygame : local, contre l'IA, ou en ligne."""

from __future__ import annotations

import sys
import threading

import pygame

from .ai import best_move
from .board import EMPTY, PLAYER_ONE, PLAYER_TWO, ColumnFullError, ConnectFour, InvalidColumnError
from .network import DEFAULT_PORT, PeerConnection
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
    def __init__(self, config: dict | None = None) -> None:
        config = config or {"mode": "local"}
        self.mode = config.get("mode", "local")
        self._online_config = config

        pygame.init()
        pygame.display.set_caption("Puissance 4")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 28)

        self.board = ConnectFour(rows=ROWS, cols=COLS)
        self.hover_col = COLS // 2

        # Mode "contre l'IA"
        self.ai_depth = config.get("depth", 4)
        self.ai_player = PLAYER_TWO
        self.ai_thinking = False
        self._ai_result: int | None = None

        # Mode "en ligne"
        self.my_player = PLAYER_ONE
        self.opponent_disconnected = False
        self._peer: PeerConnection | None = None
        self.connecting = False
        self.connect_error: str | None = None
        self._peer_result: PeerConnection | None = None

    # -- Rendu ---------------------------------------------------------

    def piece_color(self, player: int) -> tuple[int, int, int]:
        if player == PLAYER_ONE:
            return COLOR_PLAYER_ONE
        if player == PLAYER_TWO:
            return COLOR_PLAYER_TWO
        return COLOR_EMPTY

    def column_from_x(self, x: int) -> int:
        return max(0, min(self.board.cols - 1, x // CELL_SIZE))

    def _is_my_turn(self) -> bool:
        if self.mode == "ai":
            return self.board.current_player != self.ai_player
        if self.mode == "online":
            return self.board.current_player == self.my_player and not self.opponent_disconnected
        return True

    def _status_text(self) -> str | None:
        if self.board.game_over:
            if self.board.winner:
                return f"Joueur {self.board.winner} gagne — R pour rejouer"
            return "Match nul — R pour rejouer"
        if self.mode == "ai" and self.board.current_player == self.ai_player:
            return "L'IA réfléchit..."
        if self.mode == "online":
            if self.opponent_disconnected:
                return "Adversaire déconnecté"
            if self.board.current_player != self.my_player:
                return "Tour de l'adversaire..."
        return None

    def draw(self) -> None:
        self.screen.fill(COLOR_BG)

        can_preview = self._is_my_turn() and not self.board.game_over
        if can_preview and self.board.is_valid_column(self.hover_col):
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

        status = self._status_text()
        if status:
            msg = self.font.render(status, True, COLOR_TEXT)
            rect = msg.get_rect(center=(SCREEN_WIDTH // 2, CELL_SIZE // 2))
            self.screen.blit(msg, rect)

        pygame.display.flip()

    def _draw_connecting_screen(
        self, role: str, host_addr: str | None, port: int, error: str | None = None
    ) -> None:
        self.screen.fill(COLOR_BG)
        if error:
            lines = ["Connexion impossible", error]
        elif role == "host":
            lines = ["En attente d'un adversaire...", f"Port {port}"]
        else:
            lines = [f"Connexion à {host_addr}:{port}..."]

        y = SCREEN_HEIGHT // 2 - (len(lines) * 36) // 2
        for line in lines:
            surface = self.font.render(line, True, COLOR_TEXT)
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(surface, rect)
            y += 36
        pygame.display.flip()

    # -- Événements & logique ------------------------------------------

    def _shutdown(self) -> None:
        if self._peer:
            self._peer.close()
        pygame.quit()
        sys.exit(0)

    def _reset_game(self) -> None:
        self.board.reset()
        self.ai_thinking = False
        self._ai_result = None
        self.opponent_disconnected = False
        if self.mode == "online" and self._peer:
            self._peer.send({"type": "reset"})

    def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.board.game_over or not self._is_my_turn():
            return
        col = self.column_from_x(pos[0])
        try:
            self.board.drop_piece(col)
        except (ColumnFullError, InvalidColumnError):
            return
        if self.mode == "online" and self._peer:
            self._peer.send({"type": "move", "col": col})

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._shutdown()

            if event.type == pygame.MOUSEMOTION:
                self.hover_col = self.column_from_x(event.pos[0])

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(event.pos)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.board.game_over:
                    self._reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self._shutdown()

    def _start_ai_move(self) -> None:
        self.ai_thinking = True
        board_snapshot = self.board.clone()

        def worker() -> None:
            self._ai_result = best_move(board_snapshot, self.ai_player, depth=self.ai_depth)

        threading.Thread(target=worker, daemon=True).start()

    def _handle_network_message(self, message: dict) -> None:
        msg_type = message.get("type")
        if msg_type == "move":
            col = message.get("col")
            if isinstance(col, int) and self.board.is_valid_column(col):
                self.board.drop_piece(col)
        elif msg_type == "reset":
            self.board.reset()
            self.opponent_disconnected = False
        elif msg_type == "disconnected":
            self.opponent_disconnected = True

    def update(self) -> None:
        if self.board.game_over:
            return

        if self.mode == "ai" and self.board.current_player == self.ai_player:
            if not self.ai_thinking:
                self._start_ai_move()
            elif self._ai_result is not None:
                col = self._ai_result
                self._ai_result = None
                self.ai_thinking = False
                self.board.drop_piece(col)

        elif self.mode == "online" and self._peer:
            for message in self._peer.poll():
                self._handle_network_message(message)

    # -- Connexion en ligne ----------------------------------------------

    def _connect_online(self) -> bool:
        role = self._online_config.get("role", "join")
        port = self._online_config.get("port", DEFAULT_PORT)
        host_addr = self._online_config.get("host")

        self.connecting = True
        self.connect_error = None

        def worker() -> None:
            try:
                if role == "host":
                    self._peer_result = PeerConnection.host(port=port)
                    self.my_player = PLAYER_ONE
                else:
                    self._peer_result = PeerConnection.join(host_addr, port=port)
                    self.my_player = PLAYER_TWO
            except OSError as exc:
                self.connect_error = str(exc)
            finally:
                self.connecting = False

        threading.Thread(target=worker, daemon=True).start()

        while self.connecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
            self._draw_connecting_screen(role, host_addr, port)
            self.clock.tick(30)

        if self.connect_error:
            self._draw_connecting_screen(role, host_addr, port, error=self.connect_error)
            pygame.time.wait(2500)
            return False

        self._peer = self._peer_result
        return True

    # -- Boucle principale -------------------------------------------------

    def run(self) -> None:
        if self.mode == "online" and not self._connect_online():
            pygame.quit()
            return

        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
