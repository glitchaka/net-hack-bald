#!/usr/bin/env python3
"""
Script masivo para envolver strings visibles en _() en todos los .c de src/.

Busca llamadas a funciones de salida al usuario (pline, You, There, Your, etc.)
y envuelve el/los string literal(es) del primer argumento en _().

Maneja strings concatenados en C: "foo " "bar" → _("foo " "bar")
"""

import re
import os
import sys
import shutil

SRC_DIR = os.path.expanduser("~/proyectos/juego/nethack-es/src")

# Funciones cuyo PRIMER argumento string hay que envolver en _()
FUNC_1ST_ARG = [
    "pline",
    "You",
    "You_cant",
    "There",
    "Your",
    "Norep",
    "verbalize",
    "verbatim",
    "raw_printf",
    "add_menu_str",
    "end_menu",
    "impossible",
    "panic",
    "config_error_add",
    "config_error_add_end",
]

# Funciones donde argumentos específicos (por posición 1-based) son strings
# que deben envolverse en _(). Formato: (nombre_funcion, [posiciones_arg...])
FUNC_NAMED_ARGS = [
    # enl_msg(prefix, present, past, suffix, ps)
    # Los args 2 y 3 (present, past) son verbos ingleses que deben traducirse
    ("enl_msg", [2, 3]),
]


def get_string_group(text, start):
    """
    Encuentra un grupo de strings literales consecutivos (C concatenation).
    Empieza en start (debe apuntar a ").
    Devuelve (end_pos, full_raw_string) o (None, None).

    Ejemplo: "foo " "bar " "baz"
    → encuentra los 3 strings y devuelve end_pos apuntando tras "baz"
    """
    i = start
    raw_parts = []

    while i < len(text) and text[i] == '"':
        # Encontrar el cierre de este string literal
        j = i + 1
        while j < len(text):
            if text[j] == "\\":
                j += 2  # carácter escapado
            elif text[j] == '"':
                j += 1  # comilla de cierre
                break
            elif text[j] == "\n":
                # String multilínea con \ antes del salto
                # En C, "foo\"newline" es legal
                j += 1
            else:
                j += 1

        raw_parts.append(text[i:j])
        i = j

        # Saltar whitespace entre strings concatenados
        while i < len(text) and text[i] in " \t\n\r":
            i += 1

        # Si el siguiente char no es ", hemos terminado el grupo
        if i >= len(text) or text[i] != '"':
            break

    if not raw_parts:
        return None, None

    return i, "".join(raw_parts)


def is_already_wrapped(text, str_start):
    """
    Comprueba si el string en str_start ya está envuelto en _().
    Busca _( justo antes del string (con posibles espacios/saltos).
    """
    # Buscar _( justo antes, ignorando whitespace
    before = text[max(0, str_start - 30) : str_start]
    # Normalizar espacios
    before = re.sub(r"\s+", "", before)
    if before.endswith("_("):
        return True
    # También comprobar gettext( (aunque no debería usarse)
    if before.endswith("gettext("):
        return True
    return False


def process_file(filepath):
    """Procesa un archivo .c envolviendo strings en _()."""
    with open(filepath, "r", encoding="latin-1", errors="replace") as f:
        content = f.read()

    original = content
    changes = 0

    for func_name in FUNC_1ST_ARG:
        # Buscar función( y luego analizar argumentos
        # Usamos regex para encontrar el nombre + (
        pattern = re.compile(r"\b" + re.escape(func_name) + r"\s*\(")

        # Recolectar todas las posiciones de llamadas
        calls_to_process = []  # (str_start, str_end, full_raw, group_start)

        for match in pattern.finditer(content):
            paren_start = match.end()  # posición justo después de (

            # Analizar el primer argumento
            i = paren_start
            # Saltar whitespace
            while i < len(content) and content[i] in " \t\n\r":
                i += 1

            if i >= len(content) or content[i] != '"':
                continue  # El primer argumento no es un string literal

            group_start = i
            str_end, full_raw = get_string_group(content, i)
            if str_end is None:
                continue

            # No envolver si ya está envuelto
            if is_already_wrapped(content, group_start):
                continue

            # No envolver strings vacíos
            inner = full_raw[1:-1]  # Quitar comillas exterior
            inner_content = full_raw[1:-1]
            if not inner_content or inner_content.strip() == "":
                continue

            # No envolver si es solo un especificador de formato
            if re.match(r"^%\w+$", inner_content.strip()):
                continue

            # No envolver si es solo puntuación
            if all(c in " .,;:!?-\n\r" for c in inner_content):
                continue

            # Comprobar que el string no contiene " sin escapar
            # (seguridad: si hay " dentro, es probable que sea un falso positivo)
            unquoted = full_raw[1:-1]
            if '"' in unquoted:
                continue

            calls_to_process.append((group_start, str_end, full_raw))

        # Procesar de derecha a izquierda para no invalidar offsets
        for str_start, str_end, full_raw in reversed(calls_to_process):
            short = full_raw[:70] + ("..." if len(full_raw) > 70 else "")
            print(f"  {func_name}: {short}")
            replacement = "_(" + full_raw + ")"
            content = content[:str_start] + replacement + content[str_end:]
            changes += 1

    for func_name, arg_positions in FUNC_NAMED_ARGS:
        pattern = re.compile(r"\b" + re.escape(func_name) + r"\s*\(")
        calls_to_process = []

        for match in pattern.finditer(content):
            paren_start = match.end()

            # Parsear argumentos separados por coma, respetando parentesis anidados
            args = []
            depth = 0
            arg_start = paren_start
            i = paren_start
            while i < len(content) and depth >= 0:
                ch = content[i]
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth < 0:
                        break  # Fin de la llamada
                elif ch == "," and depth == 1:
                    args.append(content[arg_start:i])
                    arg_start = i + 1
                elif ch in "\"'" and (i == arg_start or content[i - 1] != "\\"):
                    # Saltar strings, no confundir comas dentro de strings
                    pass
                i += 1
            if depth < 0:
                args.append(content[arg_start : i - 1])  # Ultimo argumento

            # Intentar de otra forma: parsear saltando strings y parentesis
            # Mas robusto: usar get_string_group para argumentos string
            if len(args) < max(arg_positions):
                continue

            # Para cada posicion de argumento especificada
            for arg_pos in arg_positions:
                if arg_pos > len(args):
                    continue
                arg = args[arg_pos - 1].strip()
                # El argumento debe ser un string literal
                if not arg.startswith('"') or arg.startswith('_("'):
                    continue
                if is_already_wrapped(content, content.find(arg, match.start())):
                    continue
                # Encontrar posicion exacta en el contenido
                search_start = match.start()
                while True:
                    pos = content.find(arg, search_start)
                    if pos == -1:
                        break
                    if not is_already_wrapped(content, pos):
                        calls_to_process.append((pos, pos + len(arg), arg))
                        break
                    search_start = pos + 1

        for str_start, str_end, full_raw in reversed(calls_to_process):
            short = full_raw[:70] + ("..." if len(full_raw) > 70 else "")
            print(f"  {func_name}[arg{arg_pos}]: {short}")
            replacement = "_(" + full_raw + ")"
            content = content[:str_start] + replacement + content[str_end:]
            changes += 1

    if changes > 0:
        backup = filepath + ".bak"
        if not os.path.exists(backup):
            shutil.copy2(filepath, backup)

        with open(filepath, "w", encoding="latin-1") as f:
            f.write(content)

        print(f"  → {changes} cambios en {os.path.basename(filepath)}")

    return changes


def main():
    total_changes = 0
    files_changed = 0

    for filename in sorted(os.listdir(SRC_DIR)):
        if not filename.endswith(".c"):
            continue

        filepath = os.path.join(SRC_DIR, filename)
        print(f"\n=== {filename} ===")

        try:
            changes = process_file(filepath)
            if changes > 0:
                files_changed += 1
                total_changes += changes
        except Exception as e:
            import traceback

            print(f"  ERROR: {e}")
            traceback.print_exc()

    print(f"\n\n=== RESUMEN ===")
    print(f"Archivos modificados: {files_changed}")
    print(f"Total strings envueltos: {total_changes}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
