#!/bin/bash
# auto-translate.sh - Pipeline de traducción multi-idioma
# Uso: ./auto-translate.sh [codigo_idioma]
#   Si no se especifica idioma, usa ${LANG:0:2} o "es" por defecto

set -e

cd "$(dirname "$0")"
LANG_CODE="${1:-${LANG:0:2}}"
LANG_CODE="${LANG_CODE:-es}"  # fallback: español
INSTALL_DIR="${NETHACKDIR:-$HOME/.local/games/nethack-es}"

echo "🎯 Pipeline de Traducción - Idioma: $LANG_CODE"
echo "=================================="
echo ""

# 1. Generar .pot actualizado
echo "1/5 🔄 Generando archivo .pot desde código fuente..."
if xgettext --keyword=_ --keyword=N_ --keyword=pgettext:1c,2 \
  --from-code=UTF-8 -o po/nethack.pot src/*.c include/*.h 2>/dev/null; then
    echo "   ✅ .pot generado"
else
    echo "   ⚠️  No se pudo generar .pot"
fi

# 2. Merge con .po del idioma
PO_FILE="po/${LANG_CODE}.po"
if [ ! -f "$PO_FILE" ]; then
    echo "   ⚠️  ${PO_FILE} no existe. Creando desde plantilla..."
    msginit -l "$LANG_CODE" -o "$PO_FILE" -i po/nethack.pot --no-translator 2>/dev/null || true
fi

echo "2/5 🔀 Merge .pot con ${PO_FILE}..."
if msgmerge -U "$PO_FILE" po/nethack.pot 2>/dev/null; then
    echo "   ✅ Merge completado"
fi

# 3. Validar
echo "3/5 🔍 Validando integridad..."
if msgfmt --check "$PO_FILE" 2>/dev/null; then
    echo "   ✅ Sintaxis válida"
else
    echo "   ❌ Error de sintaxis en .po"
    exit 1
fi

stats=$(msgfmt --statistics "$PO_FILE" 2>&1)
echo "   📊 $stats"

# 4. Compilar .mo
echo "4/5 ✅ Compilando a .mo..."
mkdir -p "playground/locale/${LANG_CODE}/LC_MESSAGES"
if msgfmt "$PO_FILE" -o "playground/locale/${LANG_CODE}/LC_MESSAGES/nethack.mo"; then
    echo "   ✅ .mo compilado en playground/locale/${LANG_CODE}/LC_MESSAGES/"
else
    echo "   ❌ Error compilando .mo"
    exit 1
fi

# 5. Copiar a instalación
echo "5/5 📂 Copiando a instalación..."
if [ -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR/locale/${LANG_CODE}/LC_MESSAGES"
    cp "playground/locale/${LANG_CODE}/LC_MESSAGES/nethack.mo" \
       "$INSTALL_DIR/locale/${LANG_CODE}/LC_MESSAGES/"
    echo "   ✅ .mo copiado a $INSTALL_DIR/locale/${LANG_CODE}/LC_MESSAGES/"
fi

echo ""
echo "🎉 Pipeline completado para idioma '${LANG_CODE}'!"
echo "Para jugar: LANG=${LANG_CODE}_ES.UTF-8 nethack-es"
