#!/bin/bash
# validate-spanglish.sh - Busca Spanglish en po/es.po

cd "$(dirname "$0")"

echo "=== 🔍 VALIDACIÓN DE SPANGLISH ==="
echo "Revisando po/es.po..."
echo ""

# Lista de palabras inglesas sospechosas en traducciones al español
ENGLISH_WORDS=(
    "damage" "level" "dungeon" "monster" "monsters"
    "scroll" "potion" "potion" "wand" "shield"
    "weapon" "armor" "armour" "spell" "helmet"
    "health" "mana" "xp" "experience" "boss"
    "dragon" "chest" "treasure" "trap" "door"
    "vault" "stairs" "corridor" "room" "stone"
    "attack" "defense" "speed" "power" "magic"
    "strength" "dexterity" "intelligence" "wisdom"
    "charisma" "constitution" "skill" "ability"
    "effect" "duration" "range" "target" "area"
    "player" "enemy" "ally" "party" "team"
    "quest" "mission" "task" "goal" "objective"
    "point" "points" "gold" "coins" "coins"
    "sword" "axe" "mace" "bow" "arrow"
    "staff" "robe" "cloak" "boots" "ring" "amulet"
    "guild" "temple" "shrine" "altar" "throne"
    "save" "load" "quit" "menu" "option"
)

found_any=0

for word in "${ENGLISH_WORDS[@]}"; do
    # Buscar en msgstr (traducciones al español)
    matches=$(grep -n "^msgstr.*$word" po/es.po 2>/dev/null | head -10)
    if [ -n "$matches" ]; then
        if [ $found_any -eq 0 ]; then
            echo "⚠️  Palabras inglesas encontradas en traducciones (msgstr):"
            echo ""
        fi
        found_any=1
        echo "  '$word':"
        echo "$matches" | while IFS= read -r line; do
            line_num=$(echo "$line" | cut -d: -f1)
            text=$(echo "$line" | cut -d: -f2- | head -c 80)
            echo "    Línea $line_num: $text"
        done
        echo ""
    fi
done

if [ $found_any -eq 0 ]; then
    echo "✅ No se encontraron palabras inglesas sospechosas en msgstr"
fi

echo ""
echo "=== FIN DE VALIDACIÓN ==="
