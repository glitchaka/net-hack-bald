#!/usr/bin/env python3
"""
Corrige entradas fuzzy corruptas en es.po.

Problema: msgmerge a veces empareja incorrectamente msgids antiguos con
nuevos, resultando en traducciones que no tienen nada que ver. Por ejemplo:
  #| msgid "gloved"     # ANTIGUO msgid
  msgid "god"           # NUEVO msgid (completamente diferente)
  msgstr "con guantes"  # Traducción del ANTIGUO, corrupta para el nuevo

Estas entradas están marcadas como "fuzzy" y gettext las ignora (muestra inglés).
Pero si se compila con --no-fuzzy, se mostraría la traducción incorrecta.

Solución: detectar entradas donde el msgid nuevo y el antiguo (#|) no
comparten palabras significativas, y corregirlas.

Modos de uso:
  python3 tools/fix_fuzzy.py                    # listar entradas corruptas
  python3 tools/fix_fuzzy.py --clear            # limpiar msgstr (vacío)
  python3 tools/fix_fuzzy.py --clear --backup   # limpiar + backup .po.bak
  python3 tools/fix_fuzzy.py --clear --stats    # mostrar estadísticas
  python3 tools/fix_fuzzy.py --unfuzzy          # quitar fuzzy + limpiar
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Módulo compartido de palabras
sys.path.insert(0, str(Path(__file__).resolve().parent))
from word_lists import GAME_TERMS, SPANISH_WORDS

PO_FILE = Path.home() / "proyectos/juego/nethack-es/po/es.po"
OVERLAP_THRESHOLD = 0.3  # 30% de solapamiento mínimo
MIN_SIG_WORD_LEN = 3  # palabras de menos de 3 chars se ignoran

# Palabras que son equivalentes a efectos de comparación
EQUIVALENT = {
    "you": "your",
    "your": "you",
    "don't": "do",
    "can't": "can",
    "isn't": "is",
    "aren't": "are",
    "won't": "will",
    "wasn't": "was",
    "doesn't": "does",
    "didn't": "did",
    "haven't": "have",
    "hasn't": "has",
}


def get_significant_words(text):
    """
    Extrae palabras significativas (sustantivos, verbos, adjetivos)
    ignorando placeholders (%s, %d, etc.), números, y palabras muy cortas.
    """
    # Quitar placeholders
    text = re.sub(r"%[.\w*]*", "", text)
    # Quitar números
    text = re.sub(r"\d+", "", text)
    # Quitar puntuación
    text = re.sub(r"[.,!?;:()\[\]{}\"'<>#@&|/\\^~`=\-]", " ", text)
    # Extraer palabras
    words = re.findall(r"[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+", text)

    sig = set()
    for w in words:
        wl = w.lower()
        if len(wl) >= MIN_SIG_WORD_LEN:
            # Normalizar contracciones
            wl = EQUIVALENT.get(wl, wl)
            # Ignorar términos del juego y español
            if wl not in GAME_TERMS and wl not in SPANISH_WORDS:
                sig.add(wl)
    return sig


def word_overlap(words_a, words_b):
    """Jaccard similarity entre dos conjuntos de palabras."""
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union) if union else 0.0


def parse_po_entries(content):
    """
    Parsea el .po en entradas individuales.
    Cada entrada es un dict con: lines (lista de str), raw (bloque completo),
    y campos parseados.
    """
    # Separar por líneas en blanco
    raw_entries = re.split(r"\n\n(?=#|msgid)", content)
    entries = []

    for raw in raw_entries:
        raw = raw.strip()
        if not raw:
            continue

        e = {
            "raw": raw,
            "is_fuzzy": False,
            "has_prev": False,
            "old_id": "",
            "new_id": "",
            "translation": "",
            "overlap": 1.0,  # por defecto buena
        }

        # Detectar fuzzy
        e["is_fuzzy"] = "#, fuzzy" in raw

        if not e["is_fuzzy"]:
            entries.append(e)
            continue

        # Extraer old msgid (#|)
        m_old = re.search(r'^#\| msgid "((?:[^"\\]|\\.)*)"', raw, re.MULTILINE)
        if not m_old:
            entries.append(e)
            continue

        e["has_prev"] = True
        e["old_id"] = m_old.group(1)

        # Extraer new msgid (el que NO empieza por #|)
        m_new = re.search(r'^(?!#\| )msgid "((?:[^"\\]|\\.)*)"', raw, re.MULTILINE)
        if not m_new:
            entries.append(e)
            continue
        e["new_id"] = m_new.group(1)

        # Extraer msgstr
        m_str = re.search(r'^msgstr "((?:[^"\\]|\\.)*)"', raw, re.MULTILINE)
        if m_str:
            e["translation"] = m_str.group(1)

        # Calcular solapamiento
        old_words = get_significant_words(e["old_id"])
        new_words = get_significant_words(e["new_id"])
        e["overlap"] = word_overlap(old_words, new_words)

        entries.append(e)

    return entries


def has_significant_words(entry):
    """Comprueba si el msgid nuevo contiene palabras significativas."""
    words = get_significant_words(entry["new_id"])
    return len(words) > 0


def has_old_significant_words(entry):
    """Comprueba si el msgid antiguo (#|) contiene palabras significativas."""
    words = get_significant_words(entry["old_id"])
    return len(words) > 0


def is_corrupt(entry):
    """
    Una entrada fuzzy es 'corrupta' si el solapamiento es muy bajo.

    Excluye:
    - Entradas donde NI el antiguo NI el nuevo tienen palabras significativas
      (solo placeholders como %s %d - son cambios de formato, no corrupción)
    - Entradas donde el nuevo msgid no tiene palabras significativas
      (probablemente debug/interno)
    """
    if not entry["is_fuzzy"] or not entry["has_prev"]:
        return False

    # Si ninguno tiene palabras significativas, es solo cambio de formato
    if not has_significant_words(entry) and not has_old_significant_words(entry):
        return False

    # Si el nuevo msgid no tiene palabras (solo placeholders), no es corrupta
    if not has_significant_words(entry):
        return False

    return entry["overlap"] < OVERLAP_THRESHOLD


def is_fixable(entry):
    """
    Una entrada es 'fixeable' si es corrupta Y tiene traducción.
    Si no tiene traducción, no hay nada que limpiar.
    """
    return is_corrupt(entry) and bool(entry["translation"])


def fix_entry(entry, unfuzzy=False):
    """
    Genera el texto corregido para una entrada corrupta.
    - Si unfuzzy=True: quita #, fuzzy y la línea #|
    - Si unfuzzy=False: solo limpia msgstr (lo deja vacío)
    """
    lines = entry["raw"].split("\n")
    new_lines = []

    for line in lines:
        if line.startswith("#|"):
            # Quitar línea de msgid anterior
            if unfuzzy:
                continue  # quitarla completamente
            else:
                continue  # también la quitamos
        elif unfuzzy and line.startswith("#,") and "fuzzy" in line:
            # Quitar (o modificar) la línea de flags
            rest = line.replace("fuzzy", "").strip()
            rest = rest.replace(",,", ",").strip(",").strip()
            if rest and rest != "#,":
                new_lines.append(rest)
            # si no queda nada, no añadimos línea
        elif line.startswith("msgstr ") and entry["translation"]:
            # Limpiar traducción
            new_lines.append('msgstr ""')
        else:
            new_lines.append(line)

    return "\n".join(new_lines)


def make_backup():
    """Crea backup del .po si no existe ya."""
    backup = PO_FILE.with_suffix(".po.bak")
    if not backup.exists():
        shutil.copy2(PO_FILE, backup)
        print(f"  Backup creado: {backup.name}")
        return True
    return False


def main():
    args = set(sys.argv[1:])
    do_clear = "--clear" in args
    do_unfuzzy = "--unfuzzy" in args
    do_backup = "--backup" in args
    do_stats = "--stats" in args

    content = PO_FILE.read_text(encoding="utf-8")
    entries = parse_po_entries(content)

    # Clasificar
    total_fuzzy = sum(1 for e in entries if e["is_fuzzy"])
    total_prev = sum(1 for e in entries if e["has_prev"])
    corrupt = [e for e in entries if is_corrupt(e)]
    fixable = [e for e in entries if is_fixable(e)]

    print(f"Entradas totales:          {len(entries)}")
    print(f"Fuzzy:                     {total_fuzzy}")
    print(f"Fuzzy con #|:              {total_prev}")
    print(f"Corruptas (overlap<{OVERLAP_THRESHOLD:.0%}): {len(corrupt)}")
    print(f"Fixeables (con traducción): {len(fixable)}")

    if do_stats:
        # Distribución de overlap
        bins = {"0%": 0, "1-10%": 0, "10-20%": 0, "20-30%": 0}
        for e in corrupt:
            ov = e["overlap"]
            if ov == 0:
                bins["0%"] += 1
            elif ov < 0.1:
                bins["1-10%"] += 1
            elif ov < 0.2:
                bins["10-20%"] += 1
            else:
                bins["20-30%"] += 1
        print(f"\nDistribución de solapamiento:")
        for label, count in bins.items():
            bar = "#" * (count // 5)
            print(f"  {label:>8}: {count:4d} {bar}")

    # Mostrar las peores (ordenadas por overlap ascendente)
    corrupt_sorted = sorted(corrupt, key=lambda e: e["overlap"])
    print(f"\nPeores 30 entradas corruptas:")
    print("-" * 100)
    for e in corrupt_sorted[:30]:
        ov = e["overlap"]
        old = e["old_id"][:50]
        new = e["new_id"][:50]
        tr = e["translation"][:50]
        print(f"  [{ov:.0%}] old={old:<50s}")
        print(f"        new={new:<50s}")
        print(f"        tr={tr:<50s}")
        print()

    # Acción correctiva
    if do_clear or do_unfuzzy:
        if do_backup:
            make_backup()

        # Procesar cada entrada corrupta y fixeable
        new_entries = []
        fixed = 0
        for e in entries:
            if is_fixable(e):
                fixed_entry = fix_entry(e, unfuzzy=do_unfuzzy)
                new_entries.append(fixed_entry)
                fixed += 1
            else:
                new_entries.append(e["raw"])

        new_content = "\n\n".join(new_entries) + "\n"
        PO_FILE.write_text(new_content, encoding="utf-8")

        action = "unfuzzy + limpio" if do_unfuzzy else "msgstr vacío"
        print(f"Corregidas {fixed} entradas ({action}).")
        print(f"Archivo guardado: {PO_FILE}")

        # Verificar que msgfmt sigue funcionando
        import subprocess

        result = subprocess.run(
            ["msgfmt", "-c", "-o", "/dev/null", str(PO_FILE)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ msgfmt -c: OK")
        else:
            print(f"✗ msgfmt -c: ERROR")
            print(result.stderr[:500])

    return 0 if not fixable else 0


if __name__ == "__main__":
    sys.exit(main())
