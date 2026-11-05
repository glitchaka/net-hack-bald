#!/usr/bin/env python3
"""
NetHack-es: Traduccion masiva de cadenas C restantes en combined-es.po.

Aplica un diccionario directo y patrones funcionales.

Espanol de Espana (peninsular), forma "tu".
"""

import polib
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
PO_FILE = os.path.join(PROJECT_DIR, "po/combined-es.po")
MO_FILE = os.path.join(PROJECT_DIR, "po/combined-es.mo")
PLAYGROUND_MO = os.path.join(PROJECT_DIR, "playground/locale/es/LC_MESSAGES/nethack.mo")

# =====================================================================
# Cargar diccionario directo desde TSV
# =====================================================================


def load_tsv(path):
    """Carga un archivo TSV: msgid<TAB>msgstr por linea.

    Las lineas se separan por \n. Si un msgid contiene saltos de linea
    reales, hay que escribirlos en una sola linea del TSV usando \n
    literal como caracter (esto requiere un parser mas cuidadoso).
    Aqui se usa un truco: se concatenan las lineas del archivo en un
    unico string y luego se procesan manualmente.
    """
    direct = {}
    if not os.path.isfile(path):
        return direct
    with open(path, "rb") as f:
        data = f.read()
    if not data:
        return direct
    text = data.decode("utf-8", errors="replace")
    # Parsear: cada entrada es una linea que contiene exactamente un \t
    # Si la linea no tiene \t, se omite. Esto significa que no podemos
    # representar msgids con saltos de linea reales a traves del TSV
    # directamente; se manejaran en HARDCODE a continuacion.
    for line in text.split("\n"):
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            direct[parts[0]] = parts[1]
    return direct


# Casos especiales con saltos de linea reales en el msgid
HARDCODE = {
    "\n%s": "\n%s",
    "\n%d error%s %s %s.\n": "\n%d error%s %s %s.\n",
}


# =====================================================================
# Compilar e instalar .mo
# =====================================================================


def compile_and_install():
    result = subprocess.run(
        ["msgfmt", "-o", MO_FILE, PO_FILE],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("ERROR compilando .po a .mo:")
        print(result.stderr)
        return False
    print(f"Compilado: {MO_FILE}")
    os.makedirs(os.path.dirname(PLAYGROUND_MO), exist_ok=True)
    import shutil

    shutil.copyfile(MO_FILE, PLAYGROUND_MO)
    print(f"Copiado a: {PLAYGROUND_MO}")
    return True


# =====================================================================
# Main
# =====================================================================


def main():
    tsv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "translate-bulk-c.tsv"
    )
    direct = load_tsv(tsv_path)
    direct.update(HARDCODE)
    print(
        f"Cargadas {len(direct)} traducciones del diccionario TSV (incluye hardcode)."
    )

    po = polib.pofile(PO_FILE)
    total_c = 0
    translated = 0
    untranslated_before = 0
    untranslated_after = 0
    remaining = []

    for entry in po:
        is_c = any(ref[0].startswith("src/") for ref in entry.occurrences)
        if not is_c:
            continue
        total_c += 1
        if not entry.msgstr and entry.msgid:
            untranslated_before += 1

    for entry in po:
        is_c = any(ref[0].startswith("src/") for ref in entry.occurrences)
        if not is_c:
            continue
        if entry.msgstr:
            translated += 1
            continue
        if not entry.msgid:
            continue
        if entry.msgid in direct:
            entry.msgstr = direct[entry.msgid]
            translated += 1
        else:
            remaining.append(entry.msgid)
            untranslated_after += 1

    po.save(PO_FILE)
    if not compile_and_install():
        sys.exit(1)

    print("=" * 60)
    print("Estadisticas de traduccion (cadenas C)")
    print("=" * 60)
    print(f"  Total entradas C:           {total_c}")
    print(f"  Sin traducir (antes):       {untranslated_before}")
    print(f"  Traducidas (acumulado):     {translated}")
    print(f"  Sin traducir (despues):     {untranslated_after}")
    pct = 100.0 * translated / total_c if total_c else 0
    print(f"  Porcentaje total:           {pct:.1f}%")
    if untranslated_before:
        delta = untranslated_before - untranslated_after
        print(f"  Recién traducidas esta vez: {delta}")
    print("=" * 60)
    if remaining:
        print(f"\nQuedan {len(remaining)} cadenas sin traducir. Primeras 30:")
        for s in remaining[:30]:
            print(f"  {s[:100]!r}")


if __name__ == "__main__":
    main()
