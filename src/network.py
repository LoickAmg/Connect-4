"""Couche réseau minimaliste pour le mode 2 joueurs en ligne.

Connexion TCP point-à-point (module `socket` natif, aucune dépendance externe) :
l'hôte ouvre un socket serveur et attend une connexion, l'invité s'y connecte
directement. Une fois la liaison établie, les deux pairs s'échangent des
messages JSON délimités par des sauts de ligne (coups joués, réinitialisation,
déconnexion) — pas de serveur tiers, pas de relais.
"""

from __future__ import annotations

import json
import queue
import socket
import threading

DEFAULT_PORT = 5555
BUFFER_SIZE = 4096


def create_listener(host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> tuple[socket.socket, int]:
    """Ouvre et lie un socket serveur, sans bloquer sur `accept()`.

    Renvoie le socket serveur et le port réellement utilisé (utile si `port=0`).
    """
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    actual_port = server_sock.getsockname()[1]
    return server_sock, actual_port


def accept_connection(server_sock: socket.socket) -> "PeerConnection":
    """Bloque jusqu'à la connexion d'un invité, puis ferme le socket d'écoute."""
    conn, _addr = server_sock.accept()
    server_sock.close()
    return PeerConnection(conn)


class PeerConnection:
    """Connexion TCP point-à-point avec lecture en arrière-plan (non bloquante)."""

    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock
        self._incoming: queue.Queue[dict] = queue.Queue()
        self._connected = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    @classmethod
    def host(cls, host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> "PeerConnection":
        """Ouvre un socket serveur et bloque jusqu'à ce qu'un invité se connecte."""
        server_sock, _ = create_listener(host, port)
        return accept_connection(server_sock)

    @classmethod
    def join(cls, host: str, port: int = DEFAULT_PORT, timeout: float = 10.0) -> "PeerConnection":
        """Se connecte à un hôte distant."""
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.settimeout(None)
        return cls(sock)

    def _read_loop(self) -> None:
        buffer = b""
        try:
            while True:
                chunk = self._sock.recv(BUFFER_SIZE)
                if not chunk:
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if line.strip():
                        self._incoming.put(json.loads(line.decode("utf-8")))
        except OSError:
            pass
        finally:
            self._connected = False
            self._incoming.put({"type": "disconnected"})

    def send(self, message: dict) -> None:
        if not self._connected:
            return
        data = (json.dumps(message) + "\n").encode("utf-8")
        try:
            self._sock.sendall(data)
        except OSError:
            self._connected = False

    def poll(self) -> list[dict]:
        """Renvoie tous les messages reçus depuis le dernier appel (non bloquant)."""
        messages = []
        while True:
            try:
                messages.append(self._incoming.get_nowait())
            except queue.Empty:
                break
        return messages

    @property
    def connected(self) -> bool:
        return self._connected

    def close(self) -> None:
        self._connected = False
        # shutdown() force le OS à envoyer FIN immédiatement et débloque tout
        # thread actuellement en train de lire ce socket (contrairement à un
        # simple close(), dont l'effet sur un recv() bloquant ailleurs n'est
        # pas garanti).
        try:
            self._sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self._sock.close()
        except OSError:
            pass
