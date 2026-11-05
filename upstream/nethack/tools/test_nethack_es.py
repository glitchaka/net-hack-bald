#!/usr/bin/env python3
"""
Test de traduccion al espanol de NetHack 5.0.
Ejecuta sesiones de juego automaticas y busca strings en ingles no traducidos.

Uso:
  cd playground && LANG=es.UTF-8 python3 ../tools/test_nethack_es.py
  python3 ../tools/test_nethack_es.py --session explore
  python3 ../tools/test_nethack_es.py --verbose
"""

import argparse, os, re, sys, time
from pathlib import Path

# Usar listas compartidas de palabras
sys.path.insert(0, str(Path(__file__).resolve().parent))
# flake8: noqa: E402
from word_lists import GAME_TERMS, SPANISH_WORDS, ENGLISH_WORDS, count_english_words

GAME_DIR = Path.home() / "proyectos/juego/nethack-es/playground"

CHECK_TRANSLATIONS = [
    ("¿Quieres que elija", "personaje"),
    ("Sí; empezar partida", "si"),
    ("No; elegir rol de nuevo", "no"),
    ("¿Está bien?", "ok"),
    ("de tu ", "your"),
    ("de un ", "a"),
    ("Está escrito en el Libro de", "quest"),
    ("el cruel dios Moloch", "moloch"),
    ("Amuleto de Yendor", "yendor"),
    ("el Inframundo", "inframundo"),
    (" de ", "the"),
    ("dios", "god"),
]


def clean_ansi(text):
    return re.sub(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\[\?[0-9;]*[a-z]", "", text)


def analyze_line(line):
    """Analiza una linea buscando ingles. Retorna (tiene_ingles, palabras_encontradas)."""
    text = line.strip()
    if len(text) < 8:
        return False, []
    if re.match(r"^\s*(--More--|\*+|\d+$|[-=]+\s*$)", text):
        return False, []
    if re.search(r"(Copyright|Stichting|nethack\.org|Please gather)", text, re.I):
        return False, []

    # Usar el detector compartido (menos estricto: min_english=4)
    has_eng, words, count = count_english_words(text, min_english=4)
    return has_eng, words


def run_session(commands, desc):
    """Ejecuta una sesion de test y retorna (output_clean, problemas)."""
    import pexpect

    save_dir = GAME_DIR / "save"
    if save_dir.exists():
        for f in save_dir.glob("*"):
            try:
                f.unlink()
            except:
                pass

    os.chdir(GAME_DIR)
    child = pexpect.spawn(
        "./nethack",
        timeout=10,
        encoding="utf-8",
        env={**os.environ, "LANG": "es.UTF-8", "TERM": "xterm-256color"},
        codec_errors="replace",
    )
    output = []

    class C:
        def write(self, s):
            if s:
                output.append(s)

        def flush(self):
            pass

    child.logfile_read = C()

    try:
        idx = child.expect(
            ["tutorial", "Quieres", "¿Quieres", "Shall", pexpect.TIMEOUT, pexpect.EOF],
            timeout=25,
        )
        if idx <= 1:
            child.sendline("n")
            time.sleep(1)
            child.expect(["¿Quieres", "Shall", pexpect.TIMEOUT], timeout=10)
        child.sendline("y")
        time.sleep(2)
        child.expect(["ok", "okay", "¿Está", "Is this", pexpect.TIMEOUT], timeout=8)
        child.sendline("y")
        time.sleep(2)
        commands(child)
        time.sleep(1)
        child.sendline("#quit")
        time.sleep(0.5)
        child.sendline("y")
        time.sleep(1)
    except:
        pass

    try:
        child.close()
    except:
        pass

    raw = "".join(output)
    clean = clean_ansi(raw)
    problemas = []
    for line in clean.split("\n"):
        es_ingles, palabras = analyze_line(line)
        if es_ingles:
            problemas.append((line.strip()[:120], palabras))

    return clean, problemas


def cmd_basic(child):
    child.send(" ")
    time.sleep(0.3)
    child.send(":")
    time.sleep(0.5)
    child.send(" ")
    time.sleep(0.3)
    child.send("i")
    time.sleep(1)
    child.send("q")
    time.sleep(0.3)
    child.send("C")
    time.sleep(1)
    child.send(" ")
    time.sleep(0.3)


def cmd_help(child):
    child.send("?")
    time.sleep(1)
    child.send("q")
    time.sleep(0.5)
    child.send("&")
    time.sleep(1)
    child.send("q")
    time.sleep(0.5)


def cmd_extended(child):
    for c in [
        "#version",
        "#time",
        "#dungeon",
        "#look",
        "#pray",
        "#enhance",
        "#adjust",
        "#annotate",
        "#options",
        "#monster",
    ]:
        child.sendline(c)
        time.sleep(0.3)
        child.send(" ")
        time.sleep(0.1)
        child.send("\x1b")
        time.sleep(0.1)


def cmd_explore(child):
    time.sleep(0.5)
    for _ in range(4):
        child.send("h")
        time.sleep(0.2)
    for _ in range(3):
        child.send("j")
        time.sleep(0.2)
    for _ in range(3):
        child.send("l")
        time.sleep(0.2)
    for _ in range(2):
        child.send("k")
        time.sleep(0.2)
    child.send("s")
    time.sleep(0.5)
    child.send(" ")
    child.send(".")
    time.sleep(0.5)
    child.send(":")
    time.sleep(0.5)
    child.send(" ")
    child.send("i")
    time.sleep(0.5)
    child.send("q")
    child.send("C")
    time.sleep(1)
    child.send(" ")


def main():
    parser = argparse.ArgumentParser(description="Test NetHack-es")
    parser.add_argument(
        "--session",
        choices=["basic", "help", "extended", "explore", "all"],
        default="all",
    )
    args = parser.parse_args()

    sessions = {
        "basic": ("Basicos", cmd_basic),
        "help": ("Ayuda", cmd_help),
        "extended": ("Extendidos", cmd_extended),
        "explore": ("Exploracion", cmd_explore),
    }

    if args.session == "all":
        to_run = list(sessions.values())
    else:
        to_run = [sessions[args.session]]

    all_problems = {}
    all_output = ""

    print(f"Test NetHack-es ({len(to_run)} sesiones)\n{'=' * 50}")

    for desc, fn in to_run:
        print(f"\n  [{desc}]")
        clean, problems = run_session(fn, desc)
        if clean:
            all_output += f"=== {desc} ===\n{clean}\n\n"
        if problems:
            for line, words in problems:
                key = line[:80]
                if key not in all_problems:
                    all_problems[key] = {"line": line, "words": words, "count": 0}
                all_problems[key]["count"] += 1
            print(f"  -> {len(problems)} problema(s)")
        else:
            print(f"  -> OK")

    # Verificacion positiva
    print(f"\n{'=' * 50}")
    found = sum(1 for s, _ in CHECK_TRANSLATIONS if s in all_output)
    missing = [(s, d) for s, d in CHECK_TRANSLATIONS if s not in all_output]
    print(f"Traducciones verificadas: {found}/{len(CHECK_TRANSLATIONS)}")

    # Resumen
    print(f"\n{'=' * 50}\nRESUMEN\n{'=' * 50}")
    if all_problems:
        alta = [p for p in all_problems.values() if p["count"] >= 2]
        media = [p for p in all_problems.values() if p["count"] < 2]
        print(f"\nProblemas: {len(all_problems)} unicos")
        print(f"  Alta ({len(alta)}):")
        for p in alta:
            print(f"    [{p['count']}x] {p['line'][:100]}")
            print(f"    ({', '.join(p['words'][:6])})")
        if media:
            print(f"  Media ({len(media)}):")
            for p in media:
                print(f"    [{p['count']}x] {p['line'][:100]}")
    else:
        print(f"\n  NO se detectaron strings en ingles\n")

    if missing:
        print(f"\nFaltan en output de test ({len(missing)}):")
        for s, d in missing:
            print(f"  - {d}: '{s}'")

    return 0 if not all_problems else 1


if __name__ == "__main__":
    sys.exit(main())
