"""Écran de menu : choix du mode de jeu (local, IA, en ligne)."""

from __future__ import annotations

import pygame

from .network import DEFAULT_PORT
from .settings import COLOR_BG, COLOR_TEXT, FONT_NAME, SCREEN_HEIGHT, SCREEN_WIDTH

AI_DIFFICULTIES = [
    ("Facile", 2),
    ("Moyen", 4),
    ("Difficile", 6),
]


class Menu:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.Font(FONT_NAME, 28)
        self.clock = pygame.time.Clock()
        self.state = "main"
        self.ip_input = ""
        self.error = ""

    def _draw_lines(self, lines: list[str]) -> None:
        self.screen.fill(COLOR_BG)
        y = SCREEN_HEIGHT // 2 - (len(lines) * 46) // 2
        for line in lines:
            surface = self.font.render(line, True, COLOR_TEXT)
            rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(surface, rect)
            y += 46
        pygame.display.flip()

    def run(self) -> dict | None:
        """Boucle le menu jusqu'à obtenir une configuration de partie (ou None si quitté)."""
        while True:
            self._render()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type != pygame.KEYDOWN:
                    continue

                result = self._handle_key(event)
                if result is not False:
                    return result

            self.clock.tick(30)

    def _render(self) -> None:
        if self.state == "main":
            self._draw_lines(
                [
                    "PUISSANCE 4",
                    "",
                    "1 - Deux joueurs (local)",
                    "2 - Contre l'IA",
                    "3 - Multijoueur en ligne",
                    "",
                    "Échap - Quitter",
                ]
            )
        elif self.state == "ai_difficulty":
            self._draw_lines(
                [
                    "Difficulté de l'IA",
                    "",
                    "1 - Facile",
                    "2 - Moyen",
                    "3 - Difficile (peut réfléchir quelques secondes)",
                    "",
                    "Échap - Retour",
                ]
            )
        elif self.state == "online_role":
            self._draw_lines(
                [
                    "Multijoueur en ligne",
                    "",
                    "1 - Héberger une partie",
                    "2 - Rejoindre une partie",
                    "",
                    "Échap - Retour",
                ]
            )
        elif self.state == "online_join_ip":
            self._draw_lines(
                [
                    "Adresse IP de l'hôte",
                    "",
                    f"> {self.ip_input}_",
                    "",
                    self.error,
                    "Entrée - Valider   Échap - Retour",
                ]
            )

    def _handle_key(self, event: pygame.event.Event):
        """Renvoie une config dict pour terminer, None pour quitter, ou False pour continuer."""
        if self.state == "main":
            if event.key == pygame.K_1:
                return {"mode": "local"}
            if event.key == pygame.K_2:
                self.state = "ai_difficulty"
            elif event.key == pygame.K_3:
                self.state = "online_role"
            elif event.key == pygame.K_ESCAPE:
                return None
            return False

        if self.state == "ai_difficulty":
            for index, key in enumerate((pygame.K_1, pygame.K_2, pygame.K_3)):
                if event.key == key:
                    return {"mode": "ai", "depth": AI_DIFFICULTIES[index][1]}
            if event.key == pygame.K_ESCAPE:
                self.state = "main"
            return False

        if self.state == "online_role":
            if event.key == pygame.K_1:
                return {"mode": "online", "role": "host", "port": DEFAULT_PORT}
            if event.key == pygame.K_2:
                self.state = "online_join_ip"
                self.ip_input = ""
                self.error = ""
            elif event.key == pygame.K_ESCAPE:
                self.state = "main"
            return False

        if self.state == "online_join_ip":
            if event.key == pygame.K_ESCAPE:
                self.state = "online_role"
            elif event.key == pygame.K_RETURN:
                host = self.ip_input.strip()
                if not host:
                    self.error = "Adresse IP requise"
                else:
                    return {"mode": "online", "role": "join", "host": host, "port": DEFAULT_PORT}
            elif event.key == pygame.K_BACKSPACE:
                self.ip_input = self.ip_input[:-1]
            else:
                char = event.unicode
                if char and (char.isalnum() or char in ".:"):
                    self.ip_input += char
            return False

        return False
