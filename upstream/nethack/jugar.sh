#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/playground/locale/es/LC_MESSAGES"
cp "$DIR/po/combined-es.mo" "$DIR/playground/locale/es/LC_MESSAGES/nethack.mo" 2>/dev/null
cd "$DIR/playground"
export LANG=es_ES.UTF-8
export NETHACK_LOCALE_DIR=./locale
exec ./nethack "$@"
