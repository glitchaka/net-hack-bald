#!/usr/bin/env python3
"""
Script para envolver formatos visibles de Sprintf en _().

Maneja concatenacion de strings C ("foo" "bar") correctamente.
Filtra formatos de debug, rutas de archivo, y otros no-visibles.

Uso: python3 tools/wrap_sprintf.py [--dry-run]
"""

import re, os, sys

SRC_DIR = os.path.expanduser("~/proyectos/juego/nethack-es/src")

FILTER_PATTERNS = [
    # Rutas de archivo
    r"^save/",
    r"^\.save",
    r"^%s/",
    r"^nhdat",
    r"^%%-%ds",
    r"^%%%ds",
    # Abreviaturas de estado
    r"^St:",
    r"^HP:",
    r"^Xp:",
    r"^Dlvl",
    r"^T:",
    r"^HD:",
    r"^ S:",
    r"^AC:",
    r"^Pw:",
    r"^18/",
    # Debug/interno
    r"^pid=",
    r"^\[",
    r"^<%d",
    r"^%c ",
    r"^%d ",
    r"^%ld ",
    r"^0x",
    r"^U\+",
    r"^%%%02X",
    r"^[a-z_]+\(",
    r"^worn ",
    r"^how_lost",
    r"^flagged",
    r"^leashmon",
    r"^unknown",
    r"^glorkum",
    r"^losestr:",
    r"^bot2:",
    r"^\\n%s",
    r"^No window types",
    r"^Can't locate processor",
    r"^Unrecognized",
    r"^Not a coordinate",
    r"^Erroneous map char",
    r"^Coordinates out",
    r"^Expected (a|an) ",
    r"^Cannot get variable",
    r"^Cannot set variable",
    r"^Wrong number",
    r"^Unknown u table",
    r"^Cannot set u table",
    r"^Closed for inventory",
    r"^Where is shopdoor",
    r"^Mobile light",
    r"^Placebc ",
    r"^Unplacebc ",
    r"^Lift_covet",
    r"^Invocation position",
    r"^Portal @",
    r"^Flags: 0x",
    r"^Current time",
    r"^Swallow countdown",
    r"^Vault counter",
    r"^Level is no-teleport",
    r"^Level #0 pid",
    r"^PID \(",
    r"^Cannot create",
    r"^Cannot open",
    r"^Cannot find",
    r"^Invalid %s$",
    r"^Options compiled",
    r"^Supported ",
    r"^%.40s report",
    r"^Can't start",
    r"^Error reading",
    r"^T start=",
    r"^F start=",
    r"^T %06ld",
    r"^F %06ld",
    r"^This is bones",
    r"^This is level",
    r"^Current %s hilites",
    r"^No current hilites",
    r"^OPTIONS=",
    r"^WIZKIT=",
    r"^MENUCOLOR=",
    r"^MSGTYPE=",
    r"^AUTOCOMPLETE=",
    r"^BIND=",
    r"^# NetHack config",
    r"^\\G%04X",
    r"^D:%d",
    r"^Monster%s migrating",
    r"^Unknown level flag",
    r"^Array entry",
    r"^%sSYMBOLS=",
    r"^Line %d:",
    r"^%%s boulder",
    r"^%%s obj",
    r"^%%s%%s ",
    r"^%%sown",
    r"^%%%d around",
    r"^%d top",
    r"^Doing that so many",
    r"^There is no underlying",
    r"^Multiple role values",
    r"^Bad status hilite",
    r"^For a brief explanation",
    r"^Booleans \(selecting",
    r"^Compounds \(selecting",
    r"^Variable playground",
    r"^Set what options\?",
    r"^Accept current choice",
    r"^If not on last page",
    r"^Cancel menu without",
    r"^Menu control keys:",
    r"^Exter a target string",
    r"^Boolean options \(which",
    r"^Some of the options",
    r"^Some options are stored",
    r"^To contact",
    r"^see the .Contact.",
]


def should_skip(text):
    if len(text) < 5:
        return True
    if not re.search(r"[A-Za-záéíóú]", text):
        return True
    # Solo placeholders
    if re.match(r"^[%\s\d\.,;:\-\(\)\[\]]+$", text):
        return True
    for pat in FILTER_PATTERNS:
        if re.match(pat, text):
            return True
    return False


def process_file(fpath, dry_run=False):
    with open(fpath, "r", encoding="latin-1", errors="replace") as f:
        content = f.read()

    changes = 0
    replacements = []

    # Buscar Sprintf(buf, "FORMAT"...)
    # Manejar strings en varias lineas y concatenacion C
    i = 0
    while i < len(content):
        # Buscar Sprintf(
        m = re.search(r"\bSprintf\s*\(", content[i:])
        if not m:
            break

        start = i + m.start()
        paren_start = start + m.end() - m.start()

        # Encontrar la coma que separa buf del formato
        # Saltar el primer argumento (buf)
        depth = 1
        j = paren_start
        while j < len(content) and depth > 0:
            if content[j] == "(":
                depth += 1
            elif content[j] == ")":
                depth -= 1
            elif content[j] == '"':
                # Saltar string
                j += 1
                while j < len(content) and not (
                    content[j] == '"' and content[j - 1] != "\\"
                ):
                    if content[j] == "\\":
                        j += 1
                    j += 1
            elif content[j] == "," and depth == 1:
                # Encontramos la coma que separa buf del formato
                break
            j += 1

        if depth != 1 or content[j] != ",":
            i = start + 1
            continue

        # Ahora buscar el string de formato (puede ser multilinea o concatenado)
        fmt_start = j + 1
        while fmt_start < len(content) and content[fmt_start] in " \t\n\r":
            fmt_start += 1

        if content[fmt_start] != '"':
            i = start + 1
            continue

        # El formato puede ser "texto" o "texto" "mas texto" (C concat)
        # Recopilar todos los fragmentos concatenados
        all_fmt = ""
        k = fmt_start
        concat_start = fmt_start
        concat_end = k

        while k < len(content):
            if content[k] != '"':
                break
            # String literal
            k += 1
            while k < len(content) and not (
                content[k] == '"' and content[k - 1] != "\\"
            ):
                if content[k] == "\\":
                    k += 1
                k += 1
            if k < len(content) and content[k] == '"':
                k += 1  # Cerrar comilla
                concat_end = k
            # Ver si hay concatenacion (espacios y otro string)
            save_k = k
            while k < len(content) and content[k] in " \t\n\r":
                k += 1
            if k < len(content) and content[k] == '"':
                continue  # Hay otro string para concatenar
            else:
                k = save_k
                break

        # Extraer el texto completo concatenado
        full_fmt = content[fmt_start:concat_end]

        # Extraer el contenido (sin comillas) de cada fragmento
        fmt_text = ""
        for fm in re.finditer(r'"((?:[^"\\]|\\.)*)"', full_fmt):
            fmt_text += fm.group(1)

        # Verificar si ya esta envuelto
        before = content[max(0, fmt_start - 4) : fmt_start]
        if '_("' in before:
            i = concat_end
            continue

        # Verificar si es texto visible
        if should_skip(fmt_text):
            i = concat_end
            continue

        # Envolver el formato completo en _()
        old = full_fmt
        new = "_(" + full_fmt + ")"

        replacements.append((fmt_start, concat_end, old, new, fmt_text[:50]))
        i = concat_end

    # Aplicar
    for start, end, old, new, short in sorted(replacements, reverse=True):
        if dry_run:
            print(f"  {os.path.basename(fpath)}: {short}")
        else:
            content = content[:start] + new + content[end:]
            changes += 1

    if not dry_run and changes > 0:
        with open(fpath, "w", encoding="latin-1") as f:
            f.write(content)

    return changes


def main():
    dry_run = "--dry-run" in sys.argv
    total = 0

    for fname in sorted(os.listdir(SRC_DIR)):
        if not fname.endswith(".c"):
            continue
        fpath = os.path.join(SRC_DIR, fname)
        changes = process_file(fpath, dry_run)
        if changes > 0:
            total += changes
            if not dry_run:
                print(f"  {fname}: {changes}")

    print(f"\nTotal: {total} cambios" if not dry_run else "")


if __name__ == "__main__":
    main()
