#!/usr/bin/env python3
"""Prueba de integración: menú y partida TCP para 2 a 6 héroes.
Solo se ejecuta después de que la fuente esté publicada en GitHub.
"""
from __future__ import annotations

import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def send_frame(sock: socket.socket, kind: str, text: str) -> None:
    payload = text.encode("utf-8")
    sock.sendall(kind.encode("ascii") + struct.pack(">I", len(payload)) + payload)


def read_exact(sock: socket.socket, n: int) -> bytes:
    result = bytearray()
    while len(result) < n:
        chunk = sock.recv(n - len(result))
        if not chunk:
            raise ConnectionError("Conexión cerrada antes de completar una trama")
        result.extend(chunk)
    return bytes(result)


def read_frame(sock: socket.socket) -> tuple[str, str]:
    header = read_exact(sock, 5)
    length = struct.unpack(">I", header[1:])[0]
    if length > 131072:
        raise ValueError("Trama excesiva")
    return chr(header[0]), read_exact(sock, length).decode("utf-8")


def wait_frame(sock: socket.socket, kind: str, fragment: str = "") -> str:
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        event, content = read_frame(sock)
        if event == "E":
            raise AssertionError(f"El servidor rechazó la conexión: {content}")
        if event == kind and fragment in content:
            return content
    raise TimeoutError(f"Falta trama {kind} con {fragment}")


def connect_player(port: int, name: str) -> socket.socket:
    sock = socket.create_connection(("127.0.0.1", port), timeout=12)
    sock.settimeout(12)
    send_frame(sock, "H", f"{name}\nguerrero\n")
    wait_frame(sock, "S", "JUGADORES")
    return sock


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python tests/smoke_multiplayer.py ruta_del_ejecutable")
    executable = Path(sys.argv[1]).resolve()
    assert executable.is_file(), f"No existe {executable}"

    # En modo interactivo sin argumentos debe mostrar el menú y aceptar salir.
    menu = subprocess.run(
        [str(executable)], input="5\n", capture_output=True,
        text=True, encoding="utf-8", errors="replace", timeout=15,
        check=False,
    )
    assert menu.returncode == 0, f"El menú terminó con {menu.returncode}:\n{menu.stderr}"
    assert "CREAR PARTIDA Y JUGAR" in menu.stdout, "No apareció el menú al ejecutar sin argumentos"

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = int(probe.getsockname()[1])

    with tempfile.TemporaryDirectory(prefix="nhb-multi-") as temp:
        save = str(Path(temp) / "campana.nhb")
        server = subprocess.Popen(
            [str(executable), "servidor",
             "--bind=127.0.0.1", f"--puerto={port}", f"--guardar={save}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            cwd=temp,
        )
        players: list[socket.socket] = []
        try:
            for i in range(40):
                if server.poll() is not None:
                    raise AssertionError(f"El servidor terminó con código {server.returncode}")
                try:
                    with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                        break
                except OSError:
                    time.sleep(0.10)
            else:
                raise TimeoutError("El servidor no abrió el puerto TCP")

            # Primera sesión: pantalla de espera. Segunda: mundo compartido.
            players.append(connect_player(port, "Heroe1"))
            players.append(connect_player(port, "Heroe2"))
            send_frame(players[0], "K", ".")
            wait_frame(players[0], "S", "Esperando")
            send_frame(players[1], "K", ".")
            wait_frame(players[1], "S", "Ronda 1")

            for i in range(3, 7):
                players.append(connect_player(port, f"Heroe{i}"))
            send_frame(players[0], "R", "")
            screen = wait_frame(players[0], "S", "JUGADORES (6/6)")
            assert "Heroe1" in screen and "Heroe6" in screen, "No aparecen los seis personajes"
            assert "MOCHILA:" in screen and "PV " in screen

            seventh = socket.create_connection(("127.0.0.1", port), timeout=12)
            try:
                seventh.settimeout(12)
                send_frame(seventh, "H", "Heroe7\nguerrero\n")
                event, data = read_frame(seventh)
                assert event == "E" and "seis" in data.lower(), (event, data)
            finally:
                seventh.close()

            assert Path(save).is_file(), "No se guardó el estado multijugador"
            print("OK: menú, servidor TCP, 2-6 personajes, rondas, límite y persistencia.")
            return 0
        finally:
            for player in players:
                player.close()
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == "__main__":
    sys.exit(main())
