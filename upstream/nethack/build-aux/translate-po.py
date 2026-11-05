#!/usr/bin/env python3
"""
NetHack-es: Aplica traducciones a po/es.po de forma segura.
Usa polib si está disponible, o parseo manual con escapes correctos.

Uso: python3 build-aux/translate-po.py <fichero-traducciones.txt>
"""

import sys
import os
import re
import json

PO_FILE = "po/es.po"


def parse_translations_file(filepath):
    """Lee un fichero de traducciones en formato: msgid|msgstr (una por línea)."""
    translations = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                parts = line.split("|", 1)
                msgid = parts[0].strip()
                msgstr = parts[1].strip()
                translations[msgid] = msgstr
    return translations


def escape_po_string(s):
    """Escapa una cadena para formato .po (comillas dobles y backslashes)."""
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    return s


def apply_translations(translations, output_file=None):
    """Aplica traducciones al fichero .po."""
    if output_file is None:
        output_file = PO_FILE

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Dividir en bloques de entrada (msgid/msgstr)
    blocks = content.split("\n\n")
    modified = 0
    not_found = []

    new_blocks = []
    for block in blocks:
        block = block.strip()
        if not block:
            new_blocks.append("")
            continue

        # Buscar msgid
        msgid_match = re.search(r'^msgid "((?:[^"\\]|\\.)*)"', block, re.MULTILINE)
        if not msgid_match:
            new_blocks.append(block)
            continue

        msgid = msgid_match.group(1)
        # Desescapar para comparar
        msgid_unescaped = msgid.replace('\\"', '"').replace("\\\\", "\\")

        if msgid_unescaped in translations:
            translation = translations[msgid_unescaped]
            escaped = escape_po_string(translation)

            # Reemplazar msgstr vacío
            # Buscar msgstr "" (posiblemente multilínea)
            block = re.sub(
                r'^msgstr ""$',
                f'msgstr "{escaped}"',
                block,
                count=1,
                flags=re.MULTILINE,
            )
            modified += 1

        new_blocks.append(block)

    new_content = "\n\n".join(new_blocks)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Traducciones aplicadas: {modified}")
    return modified


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 translate-po.py <fichero-traducciones.txt>")
        print("")
        print("Formato del fichero: una línea por traducción:")
        print("  msgid exacto|texto traducido")
        print("")
        print("O modo batch con --json:")
        print("  python3 translate-po.py --json traducciones.json")
        sys.exit(1)

    if sys.argv[1] == "--json":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            translations = json.load(f)
        apply_translations(translations)
    else:
        translations = parse_translations_file(sys.argv[1])
        apply_translations(translations)


if __name__ == "__main__":
    main()
