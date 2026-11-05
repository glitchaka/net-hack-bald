#!/usr/bin/env python3
"""
NetHack-es: Traduce dat/help en po/es.po de forma correcta.
Maneja escapes .po adecuadamente.
"""

import re
import os
import json

PO_FILE = "po/es.po"
HELP_TRANSLATIONS = "build-aux/help-translations.json"


def unescape_po(s):
    """Desescapa una cadena de formato .po a texto plano."""
    s = s.replace("\\n", "\n")
    s = s.replace("\\t", "\t")
    s = s.replace('\\"', '"')
    s = s.replace("\\\\", "\\")
    return s


def escape_po(s):
    """Escapa una cadena de texto plano a formato .po."""
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", "\\n")
    s = s.replace("\t", "\\t")
    return s


def parse_po_entries(content):
    """Parsea un fichero .po en entradas [(tipo, valor), ...]."""
    entries = []
    current = []

    for line in content.split("\n"):
        if line.strip() == "" and current:
            entries.append(current)
            current = []
        elif line.startswith("#:"):
            current.append(("ref", line))
        elif line.startswith('msgid "') or line.startswith('msgid ""'):
            m = re.match(r'msgid "((?:[^"\\]|\\.)*)"', line)
            if m:
                current.append(("msgid", m.group(1)))
            else:
                current.append(("text", line))
        elif line.startswith('msgstr "') or line.startswith('msgstr ""'):
            m = re.match(r'msgstr "((?:[^"\\]|\\.)*)"', line)
            if m:
                current.append(("msgstr", m.group(1)))
            else:
                current.append(("text", line))
        else:
            current.append(("text", line))

    if current:
        entries.append(current)

    return entries


def entries_to_po(entries):
    """Convierte entradas de vuelta a texto .po."""
    lines = []
    for entry in entries:
        for etype, val in entry:
            if etype == "ref":
                lines.append(val)
            elif etype == "msgid":
                lines.append(f'msgid "{val}"')
            elif etype == "msgstr":
                lines.append(f'msgstr "{val}"')
            elif etype == "text":
                lines.append(val)
        lines.append("")
    return "\n".join(lines)


def apply_translations(translations):
    """Aplica traducciones al .po."""
    with open(PO_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    entries = parse_po_entries(content)
    modified = 0
    total_help = 0

    for entry in entries:
        # Buscar si esta entrada es de dat/help
        is_help = any(etype == "ref" and "dat/help:" in val for etype, val in entry)
        if not is_help:
            continue

        total_help += 1

        # Extraer msgid plano
        msgid_raw = None
        for etype, val in entry:
            if etype == "msgid":
                msgid_raw = unescape_po(val)
                break

        if msgid_raw is None:
            continue

        # Buscar traducción
        if msgid_raw in translations:
            traducido = translations[msgid_raw]
            # Actualizar msgstr
            for i, (etype, val) in enumerate(entry):
                if etype == "msgstr":
                    entry[i] = ("msgstr", escape_po(traducido))
                    modified += 1
                    break

    new_content = entries_to_po(entries)

    with open(PO_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Total entradas dat/help: {total_help}")
    print(f"Traducciones aplicadas: {modified}")
    print(f"Sin traducir: {total_help - modified}")

    return modified


def load_translations():
    """Carga traducciones desde JSON."""
    with open(HELP_TRANSLATIONS, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_help_strings():
    """Extrae las cadenas de dat/help sin traducir para crear el JSON base."""
    with open(PO_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    entries = parse_po_entries(content)
    strings = []

    for entry in entries:
        is_help = any(etype == "ref" and "dat/help:" in val for etype, val in entry)
        if not is_help:
            continue

        for etype, val in entry:
            if etype == "msgid":
                unescaped = unescape_po(val)
                strings.append(unescaped)
                break

    return strings


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--extract":
        # Extraer cadenas para crear el JSON base
        strings = extract_help_strings()
        print("Cadenas de dat/help sin traducir:")
        print("Copia esto a build-aux/help-translations.json y añade traducciones")
        print()
        obj = {s: "" for s in strings}
        print(json.dumps(obj, indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "--translate":
        # Aplicar traducciones desde JSON
        if not os.path.exists(HELP_TRANSLATIONS):
            print(f"ERROR: {HELP_TRANSLATIONS} no encontrado.")
            print("Ejecuta primero: python3 build-aux/translate-help.py --extract")
            print("Luego rellena las traducciones en help-translations.json")
            sys.exit(1)
        translations = load_translations()
        # Filtrar solo las que tienen traducción
        translations = {k: v for k, v in translations.items() if v}
        apply_translations(translations)
        print("Hecho. Valida con: msgfmt --statistics po/es.po -o /dev/null")
    else:
        print("Uso:")
        print("  python3 build-aux/translate-help.py --extract    # Extraer cadenas")
        print(
            "  python3 build-aux/translate-help.py --translate  # Aplicar traducciones"
        )
