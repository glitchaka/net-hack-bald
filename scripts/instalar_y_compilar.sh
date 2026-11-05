#!/usr/bin/env bash
# NetHack Bald — instalación y compilación Ubuntu/Debian/WSL.
# Solo compila; NO inicia el juego ni hace pruebas.
set -Eeuo pipefail

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
step() { printf '\n==> %s\n' "$*"; }

if ! command -v apt-get >/dev/null 2>&1; then
    fail "Este script requiere Ubuntu/Debian (o WSL con Ubuntu)."
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
if [ -d "$SCRIPT_DIR/../upstream/nethack" ]; then
    ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
else
    ROOT="$HOME/proyectos/net-hack-bald"
fi

step "Instalar dependencias"
sudo apt-get update
sudo apt-get install -y build-essential cmake git curl ca-certificates \
    pkg-config libncurses-dev flex bison gettext \
    libx11-dev libxpm-dev libxt-dev libxaw7-dev zlib1g-dev libpng-dev

if [ ! -d "$ROOT/.git" ]; then
    [ ! -e "$ROOT" ] || fail "La carpeta $ROOT existe sin Git. No se sobrescribirá."
    step "Descargar código fuente"
    mkdir -p "$(dirname -- "$ROOT")"
    git clone --depth 1 --branch main \
        https://github.com/glitchaka/net-hack-bald.git "$ROOT"
else
    step "Actualizar código fuente"
    git -C "$ROOT" pull --ff-only
fi

[ -f "$ROOT/upstream/nethack/sys/unix/setup.sh" ] ||
    fail "No se encontró el motor original de NetHack."
GAME="$ROOT/upstream/nethack"

step "Configurar NetHack 5.0 original"
(
    cd "$GAME/sys/unix"
    sh setup.sh hints/linux.500
)

step "Preparar Lua"
(
    cd "$GAME"
    make fetch-lua
)

step "Compilar NetHack original"
(
    cd "$GAME"
    make
)

step "Compilar catálogo español disponible"
mkdir -p "$GAME/playground/locale/es/LC_MESSAGES"
msgfmt --check "$GAME/po/es.po" \
    -o "$GAME/playground/locale/es/LC_MESSAGES/nethack.mo"

step "Generar datos nhdat"
(
    cd "$GAME"
    make dlb
)
if [ -f "$GAME/dat/nhdat" ]; then
    cp "$GAME/dat/nhdat" "$GAME/playground/nhdat"
elif [ ! -f "$GAME/playground/nhdat" ]; then
    fail "No apareció el archivo de datos nhdat."
fi

step "Compilar el módulo C++17 del CMake actual"
cmake -S "$ROOT" -B "$ROOT/build" -DCMAKE_BUILD_TYPE=Release
cmake --build "$ROOT/build" --config Release

printf '\nCOMPILACIÓN TERMINADA\n'
printf 'Motor original: %s\n' "$GAME/playground/nethack"
printf 'Módulo C++:     %s\n' "$ROOT/build/nethack-bald-multi"
printf '\nPara iniciar el motor original:\n'
printf '  cd "%s/playground" && LANG=es.UTF-8 ./nethack\n' "$GAME"
printf '\nADVERTENCIA: el CMake actual compila el multijugador antiguo (un personaje compartido).\n'
printf 'La modalidad de 2-6 héroes independientes todavía no está integrada ni terminada.\n'
printf 'La traducción del motor original todavía es parcial.\n'
