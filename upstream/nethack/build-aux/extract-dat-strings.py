#!/usr/bin/env python3
"""
NetHack-es: Extractor de cadenas para ficheros dat/*.txt
Genera un fichero .pot para traducción con gettext.

Uso:
    python3 build-aux/extract-dat-strings.py [--output po/dat-strings.pot]

Escanea ficheros de texto plano en dat/ y extrae cada línea como
una cadena traducible. Ignora líneas vacías, comentarios y cabeceras.
"""

import os
import re
import sys
import argparse
from datetime import datetime


def is_translatable_line(line, filename):
    """Determina si una línea debe ser traducida."""
    stripped = line.strip()

    # Ignorar líneas vacías
    if not stripped:
        return False

    # Ignorar comentarios (líneas que empiezan con #)
    if stripped.startswith("#"):
        return False

    # Ignorar líneas de solo números
    if stripped.isdigit():
        return False

    # Ignorar líneas que son solo separadores
    if re.match(r"^[\-\=\_\*\.\s]+$", stripped):
        return False

    return True


def extract_from_text_file(filepath, base_dir):
    """Extrae cadenas de un fichero de texto plano."""
    strings = []
    relpath = os.path.relpath(filepath, base_dir)

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}", file=sys.stderr)
        return strings

    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if is_translatable_line(stripped, filepath):
            strings.append((i, stripped))

    return strings


def generate_pot(strings_by_file, output_file, package_name="NetHack-es"):
    """Genera fichero .pot a partir de las cadenas extraídas."""
    lines = []
    lines.append(f"# TRADUCCIONES DE {package_name.upper()}")
    lines.append(f"# Copyright (C) {datetime.now().year} NetHack-es")
    lines.append(
        f"# This file is distributed under the same license as the {package_name} package."
    )
    lines.append(f"# FIRST AUTHOR <EMAIL@ADDRESS>, {datetime.now().year}.")
    lines.append("")
    lines.append('msgid ""')
    lines.append('msgstr ""')
    lines.append(f'"Project-Id-Version: {package_name}\\n"')
    lines.append(
        f'"POT-Creation-Date: {datetime.now().strftime("%Y-%m-%d %H:%M%z")}\\n"'
    )
    lines.append('"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"')
    lines.append('"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"')
    lines.append('"Language-Team: Spanish <es@li.org>\\n"')
    lines.append('"Language: es\\n"')
    lines.append('"MIME-Version: 1.0\\n"')
    lines.append('"Content-Type: text/plain; charset=UTF-8\\n"')
    lines.append('"Content-Transfer-Encoding: 8bit\\n"')
    lines.append('"Plural-Forms: nplurals=2; plural=(n != 1);\\n"')
    lines.append("")

    # Agrupar por msgid para deduplicar (gettext standard: una entrada con múltiples referencias)
    msgid_groups = {}  # msgid -> list of (filepath, line_no)
    for filepath in sorted(strings_by_file.keys()):
        entries = strings_by_file[filepath]
        for line_no, msgid in entries:
            if msgid not in msgid_groups:
                msgid_groups[msgid] = []
            msgid_groups[msgid].append((filepath, line_no))

    # Generar entradas .pot deduplicadas
    for msgid in sorted(msgid_groups.keys()):
        refs = msgid_groups[msgid]

        # Líneas de referencia
        for filepath, line_no in refs:
            lines.append(f"#: {filepath}:{line_no}")

        # Escapar caracteres especiales
        msgid_escaped = msgid.replace("\\", "\\\\")
        msgid_escaped = msgid_escaped.replace('"', '\\"')

        lines.append(f'msgid "{msgid_escaped}"')
        lines.append('msgstr ""')
        lines.append("")

    pot_content = "\n".join(lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pot_content)

    print(f"Generado: {output_file}")
    print(f"Total cadenas extraídas: {sum(len(v) for v in strings_by_file.values())}")
    print(f"Ficheros escaneados: {len(strings_by_file)}")

    return len(strings_by_file)


def main():
    parser = argparse.ArgumentParser(
        description="Extrae cadenas traducibles de ficheros dat/*.txt de NetHack"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Ficheros a escanear (por defecto: todos los dat/*.txt excepto .lua)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="po/dat-strings.pot",
        help="Fichero de salida .pot (por defecto: po/dat-strings.pot)",
    )
    parser.add_argument(
        "--base-dir", "-b", default=".", help="Directorio base (por defecto: .)"
    )
    args = parser.parse_args()

    base_dir = os.path.abspath(args.base_dir)
    dat_dir = os.path.join(base_dir, "dat")
    output_path = os.path.join(base_dir, args.output)

    # Asegurar que el directorio po/ existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Lista de ficheros a escanear (si no se especifican, usar POTFILES.in)
    if args.files:
        target_files = []
        for f in args.files:
            if os.path.isabs(f):
                target_files.append(f)
            else:
                target_files.append(os.path.join(base_dir, f))
    else:
        # Leer la lista de POTFILES.in si existe
        potfiles = os.path.join(base_dir, "po", "POTFILES.in")
        target_files = []
        if os.path.isfile(potfiles):
            with open(potfiles, "r") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        # Incluir ficheros dat/* (texto y .lua), excluir src/* y include/* por ahora
                        if not stripped.startswith("src/") and not stripped.startswith(
                            "include/"
                        ):
                            fullpath = os.path.join(base_dir, stripped)
                            if os.path.isfile(fullpath):
                                target_files.append(fullpath)
        else:
            # Fallback: buscar en dat/ solo ficheros de texto
            if os.path.isdir(dat_dir):
                for fname in os.listdir(dat_dir):
                    path = os.path.join(dat_dir, fname)
                    if os.path.isfile(path) and not fname.startswith("."):
                        if (
                            fname.endswith(".txt")
                            or fname == "help"
                            or fname == "hh"
                            or fname == "history"
                            or "help" in fname
                            or fname.startswith("opt")
                            or fname == "usagehlp"
                            or fname == "wizhelp"
                            or fname == "symbols"
                            or fname == "license"
                        ):
                            target_files.append(path)

    strings_by_file = {}

    for filepath in target_files:
        if os.path.isfile(filepath):
            entries = extract_from_text_file(filepath, base_dir)
            if entries:
                relpath = os.path.relpath(filepath, base_dir)
                strings_by_file[relpath] = entries
        else:
            print(f"Fichero no encontrado: {filepath}", file=sys.stderr)

    if strings_by_file:
        generate_pot(strings_by_file, output_path)
    else:
        print("No se encontraron cadenas traducibles.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
