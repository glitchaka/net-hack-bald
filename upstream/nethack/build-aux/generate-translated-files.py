#!/usr/bin/env python3
"""
NetHack-es: Genera ficheros .es traducidos a partir de po/es.po.
"""

import polib
import os
import shutil

PO_FILE = "po/es.po"
DAT_DIR = "dat"
OUT_DIR = "dat-es"

# Ficheros que tienen traducciones en el .po
TEXT_FILES = [
    "help",
    "cmdhelp",
    "hh",
    "keyhelp",
    "opthelp",
    "optmenu",
    "usagehlp",
    "wizhelp",
    "history",
    "engrave.txt",
    "epitaph.txt",
    "bogusmon.txt",
    "oracles.txt",
    "rumors.tru",
    "rumors.fal",
    "symbols",
    "tribute",
]


def load_translations():
    """Carga todas las traducciones del .po, agrupadas por fichero."""
    po = polib.pofile(PO_FILE)
    translations = {}  # filename -> {line_number: translated_text}

    for entry in po:
        if not entry.msgstr:
            continue
        for ref in entry.occurrences:
            fname = ref[0].replace("dat/", "")
            line_num = int(ref[1])
            if fname not in translations:
                translations[fname] = {}
            translations[fname][line_num] = entry.msgstr

    return translations


def generate_es_file(src_path, translations, dst_path):
    """Genera un fichero .es a partir del original y las traducciones."""
    if not os.path.exists(src_path):
        print(f"  ERROR: origen no encontrado: {src_path}")
        return False

    with open(src_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    translated_lines = []
    translated_count = 0

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if i in translations and translations[i]:
            # Línea traducida
            trans = translations[i]
            # Preservar el formato (tabs, espacios iniciales)
            prefix = line[: len(line) - len(line.lstrip())]
            translated_lines.append(f"{prefix}{trans}\n")
            translated_count += 1
        else:
            # Línea sin traducción, mantener original
            translated_lines.append(line)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    return translated_count


def main():
    print("=== Generando ficheros .es traducidos ===\n")
    translations = load_translations()

    # Limpiar directorio de salida
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR)

    total_translated = 0
    total_lines = 0

    for fname in TEXT_FILES:
        src_path = os.path.join(DAT_DIR, fname)
        dst_path = os.path.join(OUT_DIR, f"{fname}.es")

        if not os.path.exists(src_path):
            # Intentar sin sufijo
            base = os.path.splitext(fname)[0]
            alt_src = os.path.join(DAT_DIR, base)
            if os.path.exists(alt_src):
                src_path = alt_src
            else:
                print(f"  {fname:25s} → SKIP (origen no encontrado)")
                continue

        file_translations = translations.get(fname, {})
        count = generate_es_file(src_path, file_translations, dst_path)

        if os.path.exists(dst_path):
            lines = sum(1 for _ in open(dst_path, "r"))
            total_lines += lines
            trans_pct = (count / lines * 100) if lines > 0 else 0
            print(
                f"  {fname:25s} → {count:5d}/{lines:5d} líneas traducidas ({trans_pct:.0f}%)"
            )
            total_translated += count
        else:
            print(f"  {fname:25s} → ERROR al generar")

    print(f"\n  TOTAL: {total_translated}/{total_lines} líneas traducidas")
    print(f"  Directorio: {OUT_DIR}/")
    print(f"\n  Para usar: copia los ficheros a dat/ o modifica fopen_datafile()")


if __name__ == "__main__":
    main()
