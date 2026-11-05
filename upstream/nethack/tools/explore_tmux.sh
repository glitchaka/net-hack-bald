#!/bin/bash
# Explorador de NetHack con tmux - entrada en TODOS los menús y submenús
# Uso: cd playground && LANG=es.UTF-8 ../tools/explore_tmux.sh
# 
# Alternativa sin tmux: instálalo con: sudo apt install tmux

SESSION="nethack_es_$$"
LOG_DIR="/tmp/nethack_tmux_$$"
mkdir -p "$LOG_DIR"

# Limpiar sesión anterior si existe
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Limpiar saves
rm -f save/* 2>/dev/null || true

echo "============================================================"
echo "EXPLORADOR NETHACK-ES CON TMUX"
echo "============================================================"
echo "Logs: $LOG_DIR"
echo ""

# ─── Iniciar juego ───
tmux new-session -d -s "$SESSION" -x 132 -y 50 "LANG=es.UTF-8 ./nethack"
sleep 3

# ─── Funciones ───

capture() {
    local label="$1"
    local file="$LOG_DIR/${label}.txt"
    tmux capture-pane -t "$SESSION" -p -S -500 > "$file"
    echo "  📸 $label"
}

key() {
    tmux send-keys -t "$SESSION" "$1"
    sleep 0.4
}

keys() {
    tmux send-keys -t "$SESSION" "$1"
    sleep 0.2
}

enter() {
    tmux send-keys -t "$SESSION" Enter
    sleep 0.5
}

clear_more() {
    local max=20
    local count=0
    while [ $count -lt $max ]; do
        if tmux capture-pane -t "$SESSION" -p | grep -q "\-\-More\-\-"; then
            keys " "
            count=$((count + 1))
        else
            break
        fi
    done
}

# ─── FASE 1: Crear personaje ───
echo "FASE 1: Crear personaje"
echo "-----------------------"

sleep 2
capture "00_inicio"

# Auto-selección
key "y"
sleep 2
capture "01_autoseleccion"

# Confirmar
key "y"
sleep 3
capture "02_confirmacion"

# Responder tutorial
sleep 1
capture "03_tutorial"
key "n"
sleep 2

# Pasar mensajes iniciales
for i in {1..20}; do
    keys " "
done
clear_more
sleep 2
capture "04_juego"

# ─── FASE 2: Menú de Ayuda (?) y submenús ───
echo ""
echo "FASE 2: Menú de Ayuda"
echo "---------------------"

# ? - Menú principal de ayuda
key "?"
clear_more
capture "10_ayuda_principal"

# ?c - Comandos
key "c"
clear_more
capture "11_ayuda_comandos"
key "q"

# ?h - Historial
key "h"
clear_more
capture "12_historia"
key "q"

# ?k - Teclas
key "k"
clear_more
capture "13_ayuda_teclas"
key "q"

# ?o - Opciones
key "o"
clear_more
capture "14_ayuda_opciones"
key "q"

# ?m - Menú de ayuda principal otra vez (a veces sale diferente)
key "?"
clear_more
capture "15_ayuda_otra_vez"
key "q"

# ?s - Buscar en ayuda (no siempre disponible)
key "?"
sleep 0.5
key "s"
sleep 1
clear_more
capture "16_buscar_ayuda"
# Salir del modo búsqueda
keys "q"
sleep 0.3

# Volver al menú principal de ayuda y salir
key "?"
sleep 0.3
key "q"

# ─── FASE 3: Comandos extendidos (&) ───
echo ""
echo "FASE 3: Comandos extendidos"
echo "---------------------------"

key "&"
clear_more
capture "20_comandos_extendidos"
key "q"

# ─── FASE 4: Opciones del juego ───
echo ""
echo "FASE 4: Opciones"
echo "----------------"

key "#options"
clear_more
capture "30_opciones"

# Dentro de opciones navegar y salir
key "q"

# ─── FASE 5: Ayuda de opciones (?o) ───
echo ""
echo "FASE 5: Ayuda de opciones"
echo "-------------------------"

key "?o"
clear_more
capture "35_ayuda_opciones_detalle"
key "q"

# ─── FASE 6: Atributos, inventario, estado ───
echo ""
echo "FASE 6: Atributos e inventario"
echo "------------------------------"

# Atributos (C)
key "C"
clear_more
capture "40_atributos"
key " "

# Inventario (i)
key "i"
clear_more
capture "41_inventario"
key "q"

# Mirar alrededor (:)
key ":"
clear_more
capture "42_mirar"
key " "

# Mazmorra (#dungeon)
key "#dungeon"
clear_more
capture "43_mazmorra"
key " "

# Tiempo (#time)
key "#time"
clear_more
capture "44_tiempo"
key " "

# Versión (#version)
key "#version"
clear_more
capture "45_version"
key " "

# ─── FASE 7: Más comandos extendidos ───
echo ""
echo "FASE 7: Más comandos"
echo "--------------------"

# #monster (lista de monstruos)
key "#monster"
clear_more
capture "50_monstruos"
key "q"

# #dip
key "#dip"
sleep 1
clear_more
capture "51_dip"
key "\x1b"  # escape para cancelar

# #loot
key "#loot"
sleep 1
clear_more
capture "52_loot"
key "\x1b"

# #tip
key "#tip"
sleep 1
clear_more
capture "53_tip"
key "\x1b"

# #offer
key "#offer"
sleep 1
clear_more
capture "54_ofrecer"
key "\x1b"

# #pray
key "#pray"
sleep 1
clear_more
capture "55_rezar"
key "\x1b"

# #sit
key "#sit"
sleep 1
clear_more
capture "56_sentarse"
key "\x1b"

# #enhance
key "#enhance"
clear_more
capture "57_mejorar"
key "q"

# #adjust
key "#adjust"
sleep 1
clear_more
capture "58_ajustar"
key "\x1b"

# #annotate
key "#annotate"
sleep 1
clear_more
capture "59_anotar"
key "\x1b"

# #version
key "#version"
clear_more
capture "60_version2"
key " "

# #time
key "#time"
clear_more
capture "61_tiempo2"
key " "

# #history
key "#history"
clear_more
capture "62_historial2"
key "q"

# #search
key "#search"
sleep 1
clear_more
capture "63_buscar_extendido"
key "\x1b"

# #turn
key "#turn"
sleep 1
clear_more
capture "64_turno"
key "\x1b"

# #therecmdnotes (no siempre existe)
key "#therecmdnotes"
sleep 1
clear_more
capture "65_notas"
key "\x1b"

# ─── FASE 8: Moverse por el mapa ───
echo ""
echo "FASE 8: Jugando"
echo "---------------"

for i in {1..5}; do key "h"; done
for i in {1..3}; do key "j"; done
for i in {1..3}; do key "l"; done
key "s"
sleep 1
clear_more
capture "70_buscar_mapa"

key "."
clear_more
capture "71_esperar"

# Mirar entorno
key ":"
clear_more
capture "72_mirar_entorno"
key " "

# Atributos final
key "C"
clear_more
capture "73_atributos_final"
key " "

# Inventario final
key "i"
clear_more
capture "74_inventario_final"
key "q"

# ─── FASE 9: Salir ───
echo ""
echo "FASE 9: Salir"
echo "-------------"

key "#quit"
sleep 1
capture "80_confirmar_salir"
key "y"
sleep 2

# Capturar pantalla final
capture "90_fin"

# Cerrar tmux
tmux kill-session -t "$SESSION"

# ─── FASE 10: Análisis con Python ───
echo ""
echo "============================================================"
echo "ANÁLISIS DE INGLÉS"
echo "============================================================"
echo ""

# Usar el script Python de análisis si existe
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/word_lists.py" ]; then
    python3 -c "
import re, sys
sys.path.insert(0, '$SCRIPT_DIR')
from word_lists import GAME_TERMS, SPANISH_WORDS, ENGLISH_WORDS

import os
logdir = '$LOG_DIR'

all_issues = []
total_files = 0
clean_files = 0

for fname in sorted(os.listdir(logdir)):
    if not fname.endswith('.txt'):
        continue
    total_files += 1
    fpath = os.path.join(logdir, fname)
    with open(fpath, encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    lines = content.split('\n')
    file_issues = []
    for line in lines:
        text = line.strip()
        if len(text) < 8:
            continue
        if re.match(r'^\s*(--More--|\*+|\d+\$|[-=]+\s*\$)', text):
            continue
        if 'Copyright' in text or 'Stichting' in text or 'nethack.org' in text:
            continue
        
        # Detectar inglés
        words = re.findall(r'[a-zA-Z]+', text.lower())
        eng = [w for w in words if w not in GAME_TERMS and w not in SPANISH_WORDS and w in ENGLISH_WORDS]
        
        if len(eng) >= 3:
            file_issues.append((text[:120], eng[:5]))
    
    if file_issues:
        label = fname.replace('.txt', '')
        all_issues.append((label, file_issues))
        print(f'⚠  [{label}] {len(file_issues)} líneas con posible inglés:')
        for txt, words in file_issues[:5]:
            print(f'    \"{txt}\"')
            print(f'    ({', '.join(words)})')
        if len(file_issues) > 5:
            print(f'    ... y {len(file_issues)-5} más')
    else:
        clean_files += 1

print()
print('=' * 60)
print('RESUMEN')
print('=' * 60)
print(f'Pantallas capturadas: {total_files}')
print(f'Limpias:              {clean_files}')
print(f'Con posible inglés:   {len(all_issues)}')

if all_issues:
    print()
    print('Peores pantallas:')
    for label, issues in sorted(all_issues, key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f'  {label}: {len(issues)} líneas')

print()
print(f'Capturas guardadas en: {logdir}')
print('Para ver una captura: cat {logdir}/04_juego.txt')
" 2>&1
else
    # Fallback a grep básico
    echo "(Análisis básico con grep - instala word_lists.py para mejor detección)"
    for f in "$LOG_DIR"/*.txt; do
        label=$(basename "$f" .txt)
        eng=$(grep -cE '\b(the|your|you|are|were|have|has|is|was|can|will|would|should|must|may|to|from|with|and|or|but|in|on|at|by|for|of|this|that|it|my|his|her|their|our|not|no)\b' "$f" 2>/dev/null || echo 0)
        if [ "$eng" -gt 8 ]; then
            echo "⚠  [$label] $eng palabras inglesas"
        else
            echo "✓  [$label] OK"
        fi
    done
fi
