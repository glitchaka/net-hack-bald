#!/usr/bin/env python3
"""
Script para envolver arrays de strings estáticos con N_()
y sus usos con _().

Patrón 1 (arrays):
  static const char *const nombre[] = { "texto", ... };
  → N_("texto")

Patrón 2 (usos en funciones de salida):
  pline(pltname[idx]);
  → pline(_(pltname[idx]));

Uso: python3 tools/wrap_arrays.py [--dry-run] [--wrap-usages]
"""

import re
import os
import sys

SRC_DIR = os.path.expanduser("~/proyectos/juego/nethack-es/src")

# Archivos a procesar
TARGET_FILES = [
    "eat.c",
    "trap.c",
    "zap.c",
    "pray.c",
    "apply.c",
    "potion.c",
    "cmd.c",
    "pickup.c",
    "shk.c",
    "fountain.c",
    "dig.c",
    "sounds.c",
    "engrave.c",
    "uhitm.c",
    "hack.c",
    "priest.c",
    "vault.c",
    "wield.c",
    "teleport.c",
    "mhitu.c",
    "mon.c",
    "muse.c",
    "sit.c",
    "detect.c",
    "lock.c",
    "mcastu.c",
    "polyself.c",
    "steed.c",
    "dokick.c",
    "timeout.c",
]

# Funciones que muestran texto al usuario (args envueltos en _())
DISPLAY_FUNCS = [
    "pline",
    "You",
    "You_cant",
    "You_feel",
    "You_hear",
    "You_see",
    "Your",
    "There",
    "Norep",
    "verbalize",
    "urgent_pline",
    "raw_printf",
    "add_menu_str",
    "end_menu",
    "impossible",
    "panic",
    "config_error_add",
]


def find_string_arrays(content):
    """
    Encuentra arrays de strings estáticos con N_().
    Devuelve lista de (s_start, s_end, inner_string, array_name).
    """
    # Patrón: static const char *const <nombre>[] = { ... };
    pattern = re.compile(
        r"(?:static\s+)?(?:NEARDATA\s+)?const\s+char\s+\*?\*?\s*"
        r"(\w+)\s*\[\]\s*=\s*\{"
        r"([^}]*)\}",
        re.DOTALL,
    )

    results = []
    for m in pattern.finditer(content):
        array_name = m.group(1)
        body = m.group(2)
        array_start = m.start(2)

        for sm in re.finditer(r'"((?:[^"\\]|\\.)*)"', body):
            inner = sm.group(1)
            s_start = array_start + sm.start(0)
            s_end = array_start + sm.end(0)

            # Saltar ya envueltos
            before = content[max(0, s_start - 4) : s_start]
            if '_("' in before or 'N_("' in before:
                continue

            # Saltar strings técnicos
            if len(inner) < 6:
                continue
            if inner.startswith(("Copyright", "NetHack", "Stichting")):
                continue
            if "/" in inner or "\\" in inner:
                continue
            if not re.search(r"[a-zA-Záéíóú]", inner):
                continue

            results.append(
                {
                    "type": "array_string",
                    "start": s_start,
                    "end": s_end,
                    "old": content[s_start:s_end],
                    "new": "N_(" + content[s_start:s_end] + ")",
                    "array": array_name,
                    "inner": inner,
                }
            )

    return results


def find_array_usages_in_display_funcs(content):
    """
    Encuentra usos de arrays (e.g., `array[idx]`) que son argumentos
    de funciones de salida y necesitan _().
    """
    usages = []

    # Buscar todas las llamadas a funciones de visualización
    for func in DISPLAY_FUNCS:
        # Buscar función(...)
        pattern = re.compile(r"\b" + re.escape(func) + r"\s*\(")
        for m in pattern.finditer(content):
            call_start = m.start()
            paren_start = m.end()

            # Encontrar el paren de cierre
            depth = 1
            i = paren_start
            while i < len(content) and depth > 0:
                if content[i] == "(":
                    depth += 1
                elif content[i] == ")":
                    depth -= 1
                elif content[i] == '"':
                    # Saltar string literal
                    i += 1
                    while i < len(content) and not (
                        content[i] == '"' and content[i - 1] != "\\"
                    ):
                        if content[i] == "\\":
                            i += 1
                        i += 1
                i += 1

            if depth != 0:
                continue

            call_body = content[paren_start : i - 1]

            # Buscar patrones de array[...] en los argumentos
            # que NO estén ya envueltos en _()
            for am in re.finditer(r"(\w+)\s*\[([^\]]*)\]", call_body):
                arr_name = am.group(1)
                arg_body = am.group(0)
                arg_start = paren_start + am.start()
                arg_end = paren_start + am.end()

                # No envolver si ya está envuelto
                before = content[max(0, arg_start - 4) : arg_start]
                if "_(" in before:
                    continue

                # Verificar que no sea una declaración
                line_start = content.rfind("\n", 0, call_start)
                if line_start == -1:
                    line_start = 0
                line = content[line_start:call_start]
                if "static" in line or "const" in line:
                    continue

                usages.append(
                    {
                        "type": "array_usage",
                        "start": arg_start,
                        "end": arg_end,
                        "old": arg_body,
                        "new": "_(" + arg_body + ")",
                        "array": arr_name,
                    }
                )

    return usages


def process_file(fpath, dry_run=False, wrap_usages=False):
    """Procesa un archivo."""
    with open(fpath, "r", encoding="latin-1", errors="replace") as f:
        content = f.read()

    changes = 0
    replacements = []

    # 1. Envolver strings en arrays con N_()
    arr_strings = find_string_arrays(content)
    for r in arr_strings:
        replacements.append(r)
        if dry_run:
            print(f"  N_: [{r['array']}] {r['inner'][:60]}")

    # 2. Envolver usos de arrays con _() (opcional)
    if wrap_usages:
        usages = find_array_usages_in_display_funcs(content)
        for r in usages:
            # Evitar duplicados
            is_dup = any(existing["start"] == r["start"] for existing in replacements)
            if not is_dup:
                replacements.append(r)
                if dry_run:
                    print(f"  _(): [{r['array']}] {r['old'][:60]}")

    # Aplicar reemplazos (de atrás a adelante)
    for r in sorted(replacements, key=lambda x: x["start"], reverse=True):
        if not dry_run:
            content = content[: r["start"]] + r["new"] + content[r["end"] :]
            changes += 1

    if not dry_run and changes > 0:
        with open(fpath, "w", encoding="latin-1") as f:
            f.write(content)

    return changes


def main():
    dry_run = "--dry-run" in sys.argv
    wrap_usages = "--wrap-usages" in sys.argv

    if dry_run:
        print("MODO DRY RUN - solo reporte\n")

    if wrap_usages:
        print("Modo: arrays N_() + usages _()\n")
    else:
        print("Modo: solo arrays N_()\n")

    total = 0
    for fname in TARGET_FILES:
        fpath = os.path.join(SRC_DIR, fname)
        if not os.path.exists(fpath):
            continue
        changes = process_file(fpath, dry_run, wrap_usages)
        if changes > 0 or dry_run:
            status = f"{changes} cambios" if not dry_run else "(reportado)"
            print(f"  {fname}: {status}")
        total += changes

    print(f"\nTotal: {total} cambios" if not dry_run else "")


if __name__ == "__main__":
    main()
