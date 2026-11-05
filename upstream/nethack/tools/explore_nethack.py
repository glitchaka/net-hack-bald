#!/usr/bin/env python3
"""
Explorador completo de NetHack: juega una partida y captura todas las pantallas.
Detecta texto en inglés en cada pantalla y genera un informe detallado.

Uso:
  cd playground && LANG=es.UTF-8 python3 ../tools/explore_nethack.py
  python3 ../tools/explore_nethack.py --slow  # modo lento para ver mejor
  python3 ../tools/explore_nethack.py --log   # guardar log completo
"""

import argparse, os, re, sys, time
from pathlib import Path

# Usar listas compartidas de palabras
sys.path.insert(0, str(Path(__file__).resolve().parent))
from word_lists import GAME_TERMS, SPANISH_WORDS, ENGLISH_WORDS, count_english_words

import pexpect

GAME_DIR = Path.home() / "proyectos/juego/nethack-es/playground"
LOG_FILE = Path("/tmp/nethack_explore.log")


class NetHackExplorer:
    def __init__(self, slow=False, log=False):
        self.slow = slow
        self.log = log
        self.child = None
        self.screens = []
        self.findings = []

    def clean_ansi(self, text):
        """Limpia códigos ANSI preservando texto visible."""
        ansi = re.compile(
            r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\[\?[0-9;]*[a-z]|\x1b\]0;[^\x07]*\x07|\x1b\(B|\x1b\(0"
        )
        return ansi.sub("", text).replace("\r\n", "\n").replace("\r", "\n")

    def capture_screen(self, label):
        """Captura la pantalla actual y la analiza."""
        time.sleep(1.5 if self.slow else 0.8)
        try:
            data = self.child.read_nonblocking(size=20000, timeout=2)
        except:
            data = ""

        clean = self.clean_ansi(data)
        lines = [
            l.strip() for l in clean.split("\n") if l.strip() and len(l.strip()) > 3
        ]

        # Filtrar líneas de copyright
        lines = [
            l
            for l in lines
            if not any(x in l for x in ["Copyright", "Stichting", "Version 5"])
        ]

        # Guardar para el log
        self.screens.append({"label": label, "lines": lines, "raw": clean})

        # Detectar inglés usando el detector compartido
        eng_lines = []
        for line in lines:
            has_eng, words, count = count_english_words(line, min_english=3)
            if has_eng:
                eng_lines.append((line, words))

        if eng_lines:
            self.findings.append({"screen": label, "lines": eng_lines})
            print(f"⚠ [{label}] {len(eng_lines)} líneas con inglés:")
            for txt, words in eng_lines[:5]:
                print(f"    {txt[:100]}")
                print(f"    ({', '.join(words)})")
        else:
            print(f"✓ [{label}] Sin inglés")

        if self.log:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n{'=' * 60}\n{label}\n{'=' * 60}\n")
                for l in lines:
                    f.write(f"  {l}\n")

        return clean

    def send(self, cmd, wait=0.3):
        """Envía un comando."""
        self.child.sendline(cmd)
        time.sleep(wait)

    def send_key(self, key, wait=0.3):
        """Envía una tecla."""
        self.child.send(key)
        time.sleep(wait)

    def start_game(self):
        """Inicia el juego y crea un personaje."""
        # Limpiar saves
        save_dir = GAME_DIR / "save"
        if save_dir.exists():
            for f in save_dir.glob("*"):
                try:
                    f.unlink()
                except:
                    pass

        os.chdir(GAME_DIR)
        self.child = pexpect.spawn(
            "./nethack",
            timeout=15,
            encoding="utf-8",
            env={**os.environ, "LANG": "es.UTF-8", "TERM": "xterm-256color"},
            codec_errors="replace",
            dimensions=(40, 120),
        )

        # Saltar tutorial
        idx = self.child.expect(
            ["tutorial", "Quieres", "¿Quieres", "Shall", pexpect.TIMEOUT, pexpect.EOF],
            timeout=25,
        )
        if idx <= 1:
            self.send("n", 1)

        # Auto-pick character
        self.send("y", 2)

        # Confirm character
        self.child.expect(["¿Está", "Is this", pexpect.TIMEOUT], timeout=10)
        self.capture_screen("CONFIRMACIÓN PERSONAJE")
        self.send("y", 5)

        # Responder al tutorial si aparece otra vez
        try:
            idx = self.child.expect(
                ["tutorial", "Quieres", "¿Quieres", pexpect.TIMEOUT],
                timeout=3,
            )
            if idx <= 2:
                self.send("n", 1)
        except:
            pass

        # Entrar al juego
        for _ in range(15):
            self.send_key(" ", 0.3)
            try:
                self.child.read_nonblocking(size=1000, timeout=0.3)
            except:
                pass

        self.capture_screen("ENTRADA AL JUEGO")

    def explore_menus(self):
        """Explora todos los menús principales."""
        print("\n" + "=" * 60)
        print("EXPLORANDO MENÚS")
        print("=" * 60)

        # Ayuda (?)
        self.send("?")
        self.capture_screen("AYUDA (?)")
        self.send("q", 0.5)

        # Comandos extendidos (&)
        self.send("&")
        self.capture_screen("COMANDOS EXTENDIDOS (&)")
        self.send("q", 0.5)

        # Ayuda de teclas (?k)
        self.send("?k")
        self.capture_screen("AYUDA TECLAS (?k)")
        self.send("q", 0.5)

        # Ayuda de comandos (?c)
        self.send("?c")
        self.capture_screen("AYUDA COMANDOS (?c)")
        self.send("q", 0.5)

        # Historial (?h)
        self.send("?h")
        self.capture_screen("HISTORIAL (?h)")
        self.send("q", 0.5)

        # Ayuda de opciones (?o)
        self.send("?o")
        self.capture_screen("AYUDA OPCIONES (?o)")
        self.send("q", 0.5)

        # Atributos (C)
        self.send("C")
        self.capture_screen("ATRIBUTOS (C)")
        self.send_key(" ", 0.3)

        # Inventario (i)
        self.send("i")
        self.capture_screen("INVENTARIO (i)")
        self.send("q", 0.3)

        # Mirar (:)
        self.send(":")
        self.capture_screen("MIRAR (:)")
        self.send_key(" ", 0.3)

        # Mazmorra (#dungeon)
        self.send("#dungeon")
        self.capture_screen("MAZMORRA (#dungeon)")
        self.send_key(" ", 0.3)

        # Tiempo (#time)
        self.send("#time")
        self.capture_screen("TIEMPO (#time)")

        # Versión (#version)
        self.send("#version")
        self.capture_screen("VERSIÓN (#version)")
        self.send_key(" ", 0.3)

        # Opciones (#options)
        self.send("#options")
        self.capture_screen("OPCIONES (#options)")
        self.send("q", 0.5)

    def play_game(self):
        """Juega una partida breve."""
        print("\n" + "=" * 60)
        print("JUGANDO PARTIDA")
        print("=" * 60)

        # Moverse por el mapa
        print("\nMoviendo por el mapa...")
        for _ in range(5):
            self.send_key("h", 0.2)  # izquierda
        for _ in range(3):
            self.send_key("j", 0.2)  # abajo
        for _ in range(3):
            self.send_key("l", 0.2)  # derecha
        for _ in range(2):
            self.send_key("k", 0.2)  # arriba

        self.capture_screen("DESPUÉS DE MOVER")

        # Mirar entorno
        self.send(":")
        self.capture_screen("MIRAR ENTORNO")
        self.send_key(" ", 0.3)

        # Buscar (s)
        self.send("s")
        self.capture_screen("BUSCAR (s)")

        # Esperar (.)
        self.send(".")
        self.capture_screen("ESPERAR (.)")

        # Atributos otra vez
        self.send("C")
        self.capture_screen("ATRIBUTOS FINAL (C)")
        self.send_key(" ", 0.3)

    def quit_game(self):
        """Sale del juego."""
        print("\n" + "=" * 60)
        print("SALIENDO")
        print("=" * 60)

        self.send("#quit", 1)
        self.capture_screen("CONFIRMAR SALIR")
        self.send("y", 1)

        try:
            self.child.close()
        except:
            pass

    def report(self):
        """Genera informe final."""
        print("\n" + "=" * 60)
        print("INFORME FINAL")
        print("=" * 60)

        print(f"\nPantallas capturadas: {len(self.screens)}")
        print(f"Pantallas con inglés: {len(self.findings)}")

        if self.findings:
            print("\n⚠ RESUMEN DE PROBLEMAS:")
            for finding in self.findings:
                print(f"\n  [{finding['screen']}]")
                for txt, words in finding["lines"][:3]:
                    print(f"    {txt[:80]}")
                    print(f"    ({', '.join(words)})")
        else:
            print("\n✓ NO SE DETECTÓ INGLÉS EN NINGUNA PANTALLA")

        if self.log:
            print(f"\nLog completo guardado en: {LOG_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Explorador de NetHack")
    parser.add_argument("--slow", action="store_true", help="Modo lento")
    parser.add_argument("--log", action="store_true", help="Guardar log completo")
    args = parser.parse_args()

    if args.log:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write(
                f"Log de exploración NetHack - {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

    explorer = NetHackExplorer(slow=args.slow, log=args.log)

    print("=" * 60)
    print("EXPLORADOR AUTOMÁTICO DE NETHACK")
    print("=" * 60)

    explorer.start_game()
    explorer.explore_menus()
    explorer.play_game()
    explorer.quit_game()
    explorer.report()


if __name__ == "__main__":
    main()
