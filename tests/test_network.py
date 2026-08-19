"""Tests de la couche réseau (sockets TCP en boucle locale, sans pygame)."""

import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.network import PeerConnection, accept_connection, create_listener  # noqa: E402


def _wait_for(predicate, timeout: float = 5.0, interval: float = 0.02):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = predicate()
        if result:
            return result
        time.sleep(interval)
    raise AssertionError("Timeout en attendant la condition")


def test_peer_connection_exchanges_messages():
    server_sock, port = create_listener(host="127.0.0.1", port=0)
    accepted: dict = {}

    def accept_thread() -> None:
        accepted["peer"] = accept_connection(server_sock)

    thread = threading.Thread(target=accept_thread)
    thread.start()

    guest_peer = PeerConnection.join("127.0.0.1", port=port, timeout=5)
    thread.join(timeout=5)
    host_peer = accepted["peer"]

    try:
        guest_peer.send({"type": "move", "col": 3})
        messages = _wait_for(lambda: host_peer.poll() or None)
        assert messages == [{"type": "move", "col": 3}]
    finally:
        guest_peer.close()
        host_peer.close()


def test_peer_connection_reports_disconnect():
    server_sock, port = create_listener(host="127.0.0.1", port=0)
    accepted: dict = {}

    def accept_thread() -> None:
        accepted["peer"] = accept_connection(server_sock)

    thread = threading.Thread(target=accept_thread)
    thread.start()

    guest_peer = PeerConnection.join("127.0.0.1", port=port, timeout=5)
    thread.join(timeout=5)
    host_peer = accepted["peer"]

    guest_peer.close()

    messages = _wait_for(lambda: host_peer.poll() or None)
    assert {"type": "disconnected"} in messages

    host_peer.close()
