#!/usr/bin/env bash
# NetHack-es: Extract all translatable strings from NetHack
#
# Estrategia:
#   Fase 1 - Ficheros de texto plano (help, cmdhelp, data.base, etc.)
#            Se extraen línea por línea con script Python
#   Fase 2 - Ficheros Lua (cuando tengan macros Message())
#            Se extraen con xgettext --language=Lua
#   Fase 3 - Código C (cuando tenga macros _())
#            Se extrae con xgettext --language=C
#
# Uso: ./build-aux/extract-all-strings.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_DIR/po"

mkdir -p "$OUTPUT_DIR"

# FASE 1: Ficheros de texto plano
echo "[Fase 1] Extrayendo cadenas de ficheros de texto..."

python3 "$SCRIPT_DIR/extract-dat-strings.py" \
    --base-dir "$PROJECT_DIR" \
    --output "$OUTPUT_DIR/nethack.pot" \
    dat/help dat/cmdhelp dat/keyhelp dat/hh dat/opthelp \
    dat/optmenu dat/usagehlp dat/wizhelp dat/history \
    dat/oracles.txt dat/engrave.txt dat/epitaph.txt \
    dat/bogusmon.txt dat/rumors.fal dat/rumors.tru \
    dat/symbols dat/tribute dat/data.base

TOTAL=$(grep -c "^msgid " "$OUTPUT_DIR/nethack.pot" || true)
echo "  Fichero: $OUTPUT_DIR/nethack.pot"
echo "  Total cadenas extraídas: $TOTAL"
echo ""
echo "=== Extracción completada ==="
